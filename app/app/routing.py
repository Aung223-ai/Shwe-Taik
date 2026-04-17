from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/support/(?P<customer_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/chat/staff_admin/$', consumers.ChatConsumer.as_asgi()),
]