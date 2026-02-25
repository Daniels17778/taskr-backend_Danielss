from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Chat global:   ws://host/ws/chat/global/
    # Chat privado:  ws://host/ws/chat/dm_alice_bob/
    re_path(r"^ws/chat/(?P<sala>[a-zA-Z0-9_\-]+)/$", consumers.ChatConsumer.as_asgi()),
]