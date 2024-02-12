# routing.py
# from django.urls import path
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from .consumers import ChatConsumer

# websocket_urlpatterns = [
#     path('ws/chat/', ChatConsumer.as_asgi()),
# ]

# application = ProtocolTypeRouter({
#     'websocket': AuthMiddlewareStack(
#         URLRouter(
#             websocket_urlpatterns
#         )
#     ),
# })
# chat/routing.py

from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
]
