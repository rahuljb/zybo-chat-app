# yourproject/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns

# Tell Django which settings to use when ASGI loads
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Create the Django ASGI application early so that it can be used by both
# HTTP and WebSocket.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})