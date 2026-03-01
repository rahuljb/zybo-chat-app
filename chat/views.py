from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import RegisterForm, EmailAuthenticationForm
from .models import User, Message
from django.contrib import messages

def register_view(request):
    if request.user.is_authenticated:
        return redirect('user_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_online = False
            user.last_seen = timezone.now()
            user.save()

            messages.success(request, "Account created successfully. Please log in.")

            return redirect('login')

    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('user_list')

    message = None  # feedback message

    if request.method == 'POST':
        email = request.POST.get('username')  # your form uses "username" field for email
        password = request.POST.get('password')

        # 1️⃣ Check if user exists
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            message = "User does not exist. Please register."
            return render(request, 'login.html', {'form': EmailAuthenticationForm(), 'error': message})

        # 2️⃣ Validate password
        user = authenticate(request, email=email, password=password)
        if user is None:
            message = "Incorrect password. Try again."
            return render(request, 'login.html', {'form': EmailAuthenticationForm(), 'error': message})

        # 3️⃣ Success: login user
        user.is_online = True
        user.last_seen = timezone.now()
        user.save(update_fields=['is_online', 'last_seen'])

        login(request, user)
        return redirect('user_list')

    return render(request, 'login.html', {'form': EmailAuthenticationForm()})


@login_required
def logout_view(request):
    user = request.user
    user.is_online = False
    user.last_seen = timezone.now()
    user.save(update_fields=['is_online', 'last_seen'])
    logout(request)
    return redirect('login')



@login_required
def user_list_view(request):
    users = (
        User.objects
        .exclude(id=request.user.id)
        .annotate(
            unread_count=Count(
                'sent_messages',
                filter=Q(sent_messages__receiver=request.user, sent_messages__is_read=False)
            )
        )
    )
    return render(request, 'user_list.html', {
        'users': users,
        'current_user': request.user,
    })




@login_required
def chat_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # mark this conversation as read
    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    # other users with unread count
    users = (
        User.objects
        .exclude(id=request.user.id)
        .annotate(
            unread_count=Count(
                'sent_messages',
                filter=Q(
                    sent_messages__receiver=request.user,
                    sent_messages__is_read=False
                )
            )
        )
    )

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')  

    return render(request, 'chat.html', {
        'other_user': other_user,
        'chat_messages': messages,
        'users': users,
        'current_user': request.user,
    })

@login_required
def chat_home_view(request):
    # all other users with unread count
    users = (
        User.objects
        .exclude(id=request.user.id)
        .annotate(
            unread_count=Count(
                'sent_messages',
                filter=Q(
                    sent_messages__receiver=request.user,
                    sent_messages__is_read=False
                )
            )
        )
    )

    
    return render(request, 'chat.html', {
        'other_user': None,         
        'chat_messages': [],         
        'users': users,           
        'current_user': request.user,
    })