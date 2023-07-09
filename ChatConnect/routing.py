from django.urls import path
from . import consumer

websocket_urlpatterns = [
    path('send-message/<int:group_id>/', consumer.GroupChatConsumer.as_asgi()),
]
