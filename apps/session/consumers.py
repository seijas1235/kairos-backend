from channels.generic.websocket import AsyncJsonWebsocketConsumer
from apps.agents.orchestrator import Orchestrator
import logging
import json

logger = logging.getLogger(__name__)

class KairosConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for handling KAIROS session communication.
    Maintains persistent connection.
    """

    async def connect(self):
        # Initialize the Orchestrator for this session
        self.orchestrator = Orchestrator()
        await self.accept()
        logger.info("=" * 60)
        logger.info("🔌 WebSocket connected: KairosConsumer")
        logger.info("=" * 60)
        # Do not close connection here

    async def disconnect(self, close_code):
        logger.info("=" * 60)
        logger.info(f"🔴 WebSocket disconnected with code: {close_code}")
        
        # Log final agent usage stats before disconnect
        if hasattr(self, 'orchestrator'):
            logger.info("📊 FINAL AGENT USAGE STATS:")
            for agent_name, count in self.orchestrator.agent_usage_stats.items():
                status = "✅" if count > 0 else "⚪"
                logger.info(f"  {status} {agent_name}: {count} calls")
            
            total_used = sum(1 for count in self.orchestrator.agent_usage_stats.values() if count > 0)
            logger.info(f"🎯 Total: {total_used}/5 agents used in this session")
        
        logger.info("=" * 60)
        pass

    async def receive_json(self, content):
        """
        Receives JSON from Frontend, routes via Orchestrator.
        """
        try:
            # content examples:
            # {'frame': 'base64...', 'text': '...', 'style': 'Mixto'}
            # {'start_lesson': True, 'style': 'Visual'}
            
            response_data = await self.orchestrator.process_websocket_message(content)
            
            # 🔍 DEBUG: Log exact payload being sent
            logger.info(f"[DEBUG] Sending payload to frontend: {json.dumps(response_data, indent=2)}")
            
            # Format response for frontend with proper 'type' field
            formatted_response = {}
            
            # If we have content (lesson chunks), send with type="lesson_content"
            if 'content' in response_data:
                formatted_response = {
                    "type": "lesson_content",
                    "content": response_data['content']
                }
                
                # Optionally include emotion data if present
                if 'emotion' in response_data:
                    formatted_response['emotion'] = response_data['emotion']
                
                await self.send_json(formatted_response)
                logger.info(f"✅ Sent lesson_content with {len(response_data['content'])} chunks")
            
            # If we have learning_path info, send it
            if 'learning_path' in response_data:
                await self.send_json({
                    "type": "learning_path",
                    "data": response_data['learning_path']
                })
                logger.info("✅ Sent learning_path data")
            
            # Special handling for lesson_summary (final message)
            if 'lesson_summary' in response_data:
                # lesson_summary should already have "type": "lesson_summary"
                await self.send_json(response_data['lesson_summary'])
                logger.info("✅ Sent lesson_summary (final message)")
            
            # 🔍 Connection remains OPEN - ready for next message
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            await self.send_json({
                "type": "error",
                "message": "Internal server error processing your request."
            })
