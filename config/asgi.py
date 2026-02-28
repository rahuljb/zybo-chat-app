# config/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# 1️⃣ Tell Django which settings to use BEFORE importing anything that uses models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 2️⃣ Create the base Django ASGI app
django_asgi_app = get_asgi_application()

# 3️⃣ Now it is safe to import chat.routing (it will import models etc.)
from chat.routing import websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})