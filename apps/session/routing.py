"""
WebSocket URL routing for session application.
"""
from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
    re_path(
        r'ws/session/$',
        consumers.KairosConsumer.as_asgi()
    ),
]
