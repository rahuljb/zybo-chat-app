import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model

User = get_user_model()

class PresenceConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            self.close()
            return

        # A global group for presence updates
        async_to_sync(self.channel_layer.group_add)(
            "presence_group",
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_authenticated:
            async_to_sync(self.channel_layer.group_send)(
                "presence_group",
                {
                    "type": "presence_update",
                    "user_id": user.id,
                    "is_online": False
                }
            )

        async_to_sync(self.channel_layer.group_discard)(
            "presence_group",
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data or "{}")
        
        # When someone logs in → they send "online"
        if data.get("type") == "online":
            async_to_sync(self.channel_layer.group_send)(
                "presence_group",
                {
                    "type": "presence_update",
                    "user_id": data["user_id"],
                    "is_online": True
                }
            )

    def presence_update(self, event):
        self.send(text_data=json.dumps(event))