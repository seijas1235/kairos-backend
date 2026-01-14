"""
WebSocket consumer for real-time video/audio session communication.
"""
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from typing import Dict, Any


class SessionConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for real-time session communication.
    Manages WebRTC signaling for video/audio streams.
    """

    async def connect(self) -> None:
        """Accept WebSocket connection and join session room."""
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'session_{self.session_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        """Leave session room on disconnect."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data: str) -> None:
        """
        Handle incoming WebSocket messages.
        Supports WebRTC signaling: offer, answer, ice-candidate.
        """
        data = json.loads(text_data)
        message_type = data.get('type')

        # Broadcast message to all peers in the session room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'session_message',
                'message': data
            }
        )

    async def session_message(self, event: Dict[str, Any]) -> None:
        """Send message to WebSocket client."""
        message = event['message']

        await self.send(text_data=json.dumps(message))
