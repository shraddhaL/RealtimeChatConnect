"""
ASGI config for ChatConnect project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatConnect.settings')

application = get_asgi_application()

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
from ChatConnect.routing import websocket_urlpatterns


application = ProtocolTypeRouter(
    {
        'http': application,
        'websocket': URLRouter(websocket_urlpatterns),
    }
)
