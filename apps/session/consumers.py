"""
WebSocket consumer for real-time emotion detection and adaptive learning.
Integrates with multi-agent orchestrator for intelligent content adaptation.
"""
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from typing import Dict, Any
from apps.agents.orchestrator import AgentOrchestrator


class SessionConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for real-time adaptive learning sessions.
    Processes video frames and coordinates AI agents for emotion-based adaptation.
    """

    async def connect(self) -> None:
        """Accept WebSocket connection and initialize orchestrator."""
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'session_{self.session_id}'
        
        # Initialize agent orchestrator for this session
        self.orchestrator = AgentOrchestrator()

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'session_id': self.session_id,
            'message': 'Connected to KAIROS adaptive learning session'
        }))

    async def disconnect(self, close_code: int) -> None:
        """Leave session room and cleanup on disconnect."""
        # Get final analytics before cleanup
        analytics = self.orchestrator.get_session_analytics()
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Log session analytics (could save to database)
        print(f"Session {self.session_id} ended. Analytics: {analytics}")

    async def receive(self, text_data: str) -> None:
        """
        Handle incoming WebSocket messages.
        
        Message types:
        - emotion_frame: Video frame for emotion detection
        - block_completed: Student completed a content block
        - get_analytics: Request session analytics
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'emotion_frame':
                # Process frame through orchestrator
                result = await self.orchestrator.process_frame({
                    'frame': data.get('frame'),
                    'timestamp': data.get('timestamp'),
                    'current_content': data.get('current_content', {}),
                    'user_profile': data.get('user_profile', {}),
                    'topic': data.get('topic', ''),
                    'difficulty': data.get('difficulty', 'intermediate'),
                    'session_id': self.session_id
                })
                
                # Send result back to client
                await self.send(text_data=json.dumps({
                    'type': 'emotion_result',
                    **result
                }))
            
            elif message_type == 'block_completed':
                # Process block completion (triggers assessment)
                result = await self.orchestrator.process_frame({
                    'frame': data.get('frame', ''),
                    'timestamp': data.get('timestamp'),
                    'current_content': data.get('current_content', {}),
                    'user_profile': data.get('user_profile', {}),
                    'topic': data.get('topic', ''),
                    'block_completed': True,
                    'content_summary': data.get('content_summary', ''),
                    'responses': data.get('responses', []),
                    'time_spent': data.get('time_spent', 0),
                    'completed_lessons': data.get('completed_lessons', []),
                    'current_lesson': data.get('current_lesson', ''),
                    'available_lessons': data.get('available_lessons', []),
                    'session_id': self.session_id
                })
                
                await self.send(text_data=json.dumps({
                    'type': 'block_completed_result',
                    **result
                }))
            
            elif message_type == 'get_analytics':
                # Return session analytics
                analytics = self.orchestrator.get_session_analytics()
                await self.send(text_data=json.dumps({
                    'type': 'analytics',
                    **analytics
                }))
            
            elif message_type == 'reset_session':
                # Reset orchestrator for new lesson
                self.orchestrator.reset_session()
                await self.send(text_data=json.dumps({
                    'type': 'session_reset',
                    'message': 'Session state reset successfully'
                }))
            
            else:
                # Unknown message type
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error processing message: {str(e)}'
            }))

    async def session_message(self, event: Dict[str, Any]) -> None:
        """Send message to WebSocket client (for group broadcasts)."""
        message = event['message']
        await self.send(text_data=json.dumps(message))

