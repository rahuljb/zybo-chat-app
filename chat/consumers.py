import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Message

User = get_user_model()


def get_room_name(user1_id, user2_id):
    sorted_ids = sorted([int(user1_id), int(user2_id)])
    return f'chat_{sorted_ids[0]}_{sorted_ids[1]}'


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            self.close()
            return

        self.other_user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_name = get_room_name(user.id, self.other_user_id)
        self.room_group_name = f'chat_{self.room_name}'

        user.last_seen = timezone.now()
        user.save(update_fields=['last_seen'])

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        user = self.scope['user']
        if user.is_authenticated:
            user.last_seen = timezone.now()
            user.save(update_fields=['last_seen'])

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        user = self.scope['user']
        if not user.is_authenticated:
            return

        data = json.loads(text_data or "{}")
        msg_type = data.get('type')

        # mark messages as read
        if msg_type == 'read_messages':
            Message.objects.filter(
                sender_id=self.other_user_id,
                receiver=user,
                is_read=False
            ).update(is_read=True)

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'read_receipt',
                    'reader_id': user.id,
                }
            )
            return

        # typing start
        if msg_type == 'typing':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'sender_id': user.id,
                    'is_typing': True,
                }
            )
            return

        # typing stop
        if msg_type == 'stop_typing':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'sender_id': user.id,
                    'is_typing': False,
                }
            )
            return

        # delete messages
        if msg_type == 'delete_messages':
            ids = data.get('ids', [])
            if not isinstance(ids, list) or not ids:
                return

            # only delete your own messages
            qs = Message.objects.filter(
                id__in=ids,
                sender=user,
                is_deleted=False
            )

            deleted_ids = list(qs.values_list('id', flat=True))
            if not deleted_ids:
                return

            # soft delete
            qs.update(is_deleted=True)

            # notify both clients
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'message_deleted',
                    'message_ids': deleted_ids,
                    'sender_id': user.id,
                }
            )
            return

        # normal chat message
        message = data.get('message', '').strip()
        if not message:
            return

        receiver_id = int(self.other_user_id)
        receiver = User.objects.get(id=receiver_id)

        msg = Message.objects.create(
            sender=user,
            receiver=receiver,
            content=message,
            is_read=False
        )

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': msg.id,
                'message': msg.content,
                'sender_id': user.id,
                'receiver_id': receiver.id,
                'timestamp': msg.timestamp.strftime('%H:%M'),
                'is_read': msg.is_read,
            }
        )

        async_to_sync(self.channel_layer.group_send)(
            f'notifications_{receiver.id}',
            {
                'type': 'notify_message',
                'sender_id': user.id,
                'sender_name': user.username or user.email,
                'preview': msg.content[:30],
            }
        )

    def typing_indicator(self, event):
        self.send(text_data=json.dumps({
            'type': 'typing',
            'sender_id': event['sender_id'],
            'is_typing': event['is_typing'],
        }))

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))

    def read_receipt(self, event):
        self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'reader_id': event['reader_id'],
        }))

    def message_deleted(self, event):
        self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_ids': event['message_ids'],
            'sender_id': event['sender_id'],
        }))

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            self.close()
            return

        # user-specific notification group
        self.group_name = f'notifications_{user.id}'

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def notify_message(self, event):
        self.send(text_data=json.dumps(event))