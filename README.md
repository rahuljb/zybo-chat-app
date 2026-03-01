ZYBO Chat – Real-Time Messaging App
------------------------------------
ZYBO Chat is a real-time messaging application built using Django, Django Channels, WebSockets, and Bootstrap.

It features a modern chat layout inspired by popular messaging apps, including:

1.Real-time messages

2.Online / Offline presence

3.Typing indicator

4.Unread message count

5.Soft delete messages (placeholder text stays after refresh)

6.Scroll-to-bottom button

7.Clean sidebar + chat layout

8.Authentication (Register / Login / Logout)


Features
---------
Real-time WebSocket chat

Online status + last seen

Typing indicator

Unread message notifications

Soft delete messages

Stay-visible deleted message placeholders

Auto scroll button


Project Structure
-----------------

project/
│
├── chat/
│   ├── templates/
│   │   ├── base.html
│   │   ├── chat.html
│   │   ├── login.html
│   │   └── register.html
│   ├── consumers.py
│   ├── routing.py
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
│
├── project_root/
│   ├── settings.py
│   ├── asgi.py
│   └── urls.py
│
└── manage.py



1. Clone the repository

git clone git@github.com:rahuljb/zybo-chat-app.git
cd chat_app

2. Create a virtual environment

python3 -m venv venv
source venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Apply migrations

python manage.py makemigrations
python manage.py migrate

Run using Daphne (required for WebSockets):
daphne -p 8000 project_root.asgi:application

github URL:
https://github.com/rahuljb/zybo-chat-app#

host in render.com:
https://zybo-chat-app.onrender.com/login/?next=/

USER 1
email: damian@gmail.com 
password: 12345678

USER 2
email: logan@gmail.com 
password: 12345678