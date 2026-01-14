"""
WebSocket URL routing for session application.
"""
from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
    re_path(
        r'ws/v1/session/(?P<session_id>\w+)/$',
        consumers.SessionConsumer.as_asgi()
    ),
]
