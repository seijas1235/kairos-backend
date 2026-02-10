from channels.generic.websocket import AsyncJsonWebsocketConsumer
from apps.agents.orchestrator import Orchestrator
from apps.session.demo_script import run_demo_sequence
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

class KairosConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for handling KAIROS session communication.
    Maintains persistent connection.
    """

    async def connect(self):
        # Initialize the Orchestrator for this session
        self.orchestrator = Orchestrator()
        self.demo_mode_active = False  # Flag to block other messages during demo
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
        Supports: emotion frames, start_lesson, user_question, text input
        """
        try:
            logger.info("=" * 60)
            logger.info("📥 RECEIVED MESSAGE IN CONSUMER")
            logger.info(f"   Keys: {list(content.keys())}")
            logger.info(f"   Full content: {content}")
            logger.info("=" * 60)
            
            # 🚫 Block all messages if demo mode is running
            if self.demo_mode_active:
                logger.warning("⚠️ DEMO MODE ACTIVE: Ignoring incoming message")
                return
            
            # 🎬 DEMO MODE: Intercept "EVENT_HORIZON" or "EVENT HORIZON" topic
            topic = content.get('topic', '')
            # Normalize: remove spaces and convert to uppercase for comparison
            normalized_topic = topic.replace(' ', '').upper()
            logger.info(f"📨 Received message with topic: '{topic}' (normalized: '{normalized_topic}')")
            
            if 'start_lesson' in content and normalized_topic == 'EVENTHORIZON':
                logger.info("🎬🎬🎬 DEMO MODE TRIGGERED IN CONSUMER 🎬🎬🎬")
                self.demo_mode_active = True  # Block other messages
                asyncio.create_task(run_demo_sequence(self))
                return  # Skip orchestrator, use demo script instead
            
            # Log incoming message type
            msg_keys = list(content.keys())
            if 'user_question' in content:
                logger.info(f"❓ User question received: {content.get('user_question', '')[:50]}...")
            elif 'frame' in content:
                logger.info("🎭 Emotion frame received")
            elif 'start_lesson' in content:
                logger.info(f"🚀 Start lesson: {content.get('topic', 'N/A')}")

            else:
                logger.info(f"📨 Message received with keys: {msg_keys}")
            
            # Process through orchestrator
            response_data = await self.orchestrator.process_websocket_message(content)
            
            # 🎬 DEMO MODE: Check if orchestrator detected demo trigger
            if response_data.get('type') == 'demo_mode' and response_data.get('trigger'):
                logger.info("🎬🎬🎬 DEMO MODE ACTIVATED BY ORCHESTRATOR 🎬🎬🎬")
                asyncio.create_task(run_demo_sequence(self))
                return
            
            # 🔍 DEBUG: Log response type
            logger.info(f"[DEBUG] Response type: {response_data.get('type', 'N/A')}")
            
            # Handle different response types
            
            # 1. User question answers - send immediately (no streaming)
            if 'user_question' in content and 'content' in response_data:
                await self.send_json({
                    "type": "lesson_content",
                    "content": response_data['content']
                })
                logger.info("✅ Sent Q&A answer immediately")
                return
            
            # 2. Learning path info - send immediately
            if 'learning_path' in response_data:
                await self.send_json({
                    "type": "learning_path",
                    "data": response_data['learning_path']
                })
                logger.info("✅ Sent learning_path data")
                await asyncio.sleep(0.5)  # Brief pause before content
            
            # 3. Lesson content - STREAM progressively
            if 'content' in response_data:
                # Include emotion if present
                emotion_data = response_data.get('emotion')
                await self._stream_content_chunks(response_data['content'], emotion_data)
            
            # 4. Lesson summary - send immediately
            if 'lesson_summary' in response_data:
                await self.send_json(response_data['lesson_summary'])
                logger.info("✅ Sent lesson_summary (final message)")
            
            # 5. Errors
            if 'error' in response_data:
                await self.send_json({
                    "type": "error",
                    "message": response_data['error']
                })
                logger.warning(f"⚠️ Sent error: {response_data['error']}")
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}", exc_info=True)
            await self.send_json({
                "type": "error",
                "message": "Internal server error processing your request."
            })
    
    async def _stream_content_chunks(self, chunks: list, emotion_data: dict = None):
        """
        Stream content chunks progressively with reading-time delays.
        Sends one chunk at a time for a natural, readable flow.
        """
        import asyncio
        
        logger.info(f"📤 Starting stream of {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks, 1):
            # Prepare message
            message = {
                "type": "lesson_content",
                "content": [chunk]  # Send ONE chunk at a time
            }
            
            # Include emotion data only on first chunk
            if i == 1 and emotion_data:
                message['emotion'] = emotion_data
            
            # Send chunk
            await self.send_json(message)
            
            logger.info(f"📤 [{i}/{len(chunks)}] Streamed: {chunk['type']}")
            
            # Calculate reading delay
            delay = self._calculate_reading_delay(chunk)
            
            # Don't delay after last chunk
            if i < len(chunks):
                await asyncio.sleep(delay)
        
        logger.info(f"✅ Finished streaming {len(chunks)} chunks")
    
    def _calculate_reading_delay(self, chunk: dict) -> float:
        """
        Calculate appropriate delay based on chunk type and content.
        Returns delay in seconds.
        """
        chunk_type = chunk.get('type', 'text')
        
        if chunk_type == 'text':
            content = chunk.get('content', '')
            words = len(content.split())
            # Average reading speed: ~200 words/min = 3.33 words/sec
            # Add 1 second minimum for very short texts
            delay = max(2.0, words / 3.0)
            return min(delay, 8.0)  # Cap at 8 seconds
        
        elif chunk_type == 'image_prompt':
            # Images need time to view
            return 2.0
        
        elif chunk_type == 'tutor_answer':
            content = chunk.get('content', '')
            words = len(content.split())
            delay = max(2.0, words / 3.0)
            return min(delay, 10.0)  # Longer cap for answers
        
        else:
            return 1.5  # Default delay
