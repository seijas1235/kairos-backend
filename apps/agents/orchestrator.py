import logging
import json
from .emotion_agent import EmotionAgent
from .content_adapter_agent import ContentAdapterAgent
from .learning_path_agent import LearningPathAgent
from .assessment_agent import AssessmentAgent
from .personality_agent import PersonalityAgent

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Coordination center for the 5-Agent Architecture.
    Does NOT "think", only routes messages and manages flow.
    """

    def __init__(self):
        logger.info("=" * 60)
        logger.info("🎯 ORCHESTRATOR: Initializing 5-Agent System")
        logger.info("=" * 60)
        
        # Instantiate agents
        self.emotion_agent = EmotionAgent()
        self.content_adapter_agent = ContentAdapterAgent()
        self.learning_path_agent = LearningPathAgent()
        self.assessment_agent = AssessmentAgent()
        self.personality_agent = PersonalityAgent()
        
        # Track agent usage
        self.agent_usage_stats = {
            "EmotionAgent": 0,
            "ContentAdapterAgent": 0,
            "LearningPathAgent": 0,
            "AssessmentAgent": 0,
            "PersonalityAgent": 0
        }
        
        logger.info("✅ All 5 agents initialized successfully")
        logger.info("=" * 60)

    async def process_websocket_message(self, message: dict) -> dict:
        """
        Main entry point from WebSocket Consumer.
        Routing Logic:
        - key 'frame' -> EmotionAgent
        - key 'start_lesson' -> LearningPathAgent
        """
        logger.info("=" * 60)
        logger.info("📨 ORCHESTRATOR: Processing incoming message")
        logger.info(f"Message keys: {list(message.keys())}")
        logger.info("=" * 60)
        
        response_data = {}

        # 1. Handle Frame (Emotion Detection)
        if 'frame' in message:
            logger.info("🎭 Routing to: EmotionAgent")
            self.agent_usage_stats["EmotionAgent"] += 1
            
            emotion_result = await self.emotion_agent.process(message)
            response_data['emotion'] = emotion_result
            logger.info(f"✅ EmotionAgent result: {emotion_result.get('emotion', 'N/A')}")
            
            # If there's accompanying text, or if emotion triggers it, we might generate content
            # For now, let's assume we proceed to content generation if text is present
            if 'text' in message:
                logger.info("📝 Text detected, routing to: ContentAdapterAgent")
                self.agent_usage_stats["ContentAdapterAgent"] += 1
                
                content_context = {
                    "user_input": message.get('text', ''),
                    "detected_emotion": emotion_result,
                    "style": message.get('style', 'Visual') 
                }
                content_chunks = await self.content_adapter_agent.process(content_context)
                logger.info(f"✅ ContentAdapterAgent generated {len(content_chunks)} chunks")
                
                # Check for termination keywords
                user_text = message.get('text', '').lower()
                if 'terminar' in user_text or 'finish' in user_text:
                    logger.info("🏁 Termination keyword detected, routing to: AssessmentAgent")
                    self.agent_usage_stats["AssessmentAgent"] += 1
                    
                    summary = await self.assessment_agent.generate_summary({})
                    response_data['lesson_summary'] = summary
                    logger.info("✅ AssessmentAgent generated summary")
                    
                    content_chunks.append({"type": "text", "content": "Entendido, terminamos por hoy. ¡Buen trabajo!"})

                # Apply Personality
                logger.info("🎨 Routing to: PersonalityAgent (for all text chunks)")
                self.agent_usage_stats["PersonalityAgent"] += 1
                
                final_chunks = await self._apply_personality(content_chunks, emotion_result)
                response_data['content'] = final_chunks
                logger.info(f"✅ PersonalityAgent processed {len(final_chunks)} chunks")

        # 2. Handle Start Lesson
        elif 'start_lesson' in message:
            logger.info("🚀 Routing to: LearningPathAgent")
            self.agent_usage_stats["LearningPathAgent"] += 1
            
            path_result = await self.learning_path_agent.process(message)
            response_data['learning_path'] = path_result
            logger.info("✅ LearningPathAgent initialized path")
            
            # Immediately generate intro content?
            logger.info("📝 Routing to: ContentAdapterAgent (intro)")
            self.agent_usage_stats["ContentAdapterAgent"] += 1
            
            content_context = {
                "user_input": "Start Lesson",
                "detected_emotion": {"emotion": "neutral"},
                "style": message.get('style', 'Visual')
            }
            content_chunks = await self.content_adapter_agent.process(content_context)
            logger.info(f"✅ ContentAdapterAgent generated {len(content_chunks)} intro chunks")
            
            logger.info("🎨 Routing to: PersonalityAgent")
            self.agent_usage_stats["PersonalityAgent"] += 1
            
            final_chunks = await self._apply_personality(content_chunks, {"emotion": "neutral"})
            response_data['content'] = final_chunks
            logger.info(f"✅ PersonalityAgent processed {len(final_chunks)} intro chunks")

        else:
            logger.warning("❓ Unknown message type received in Orchestrator")
            response_data['error'] = "Unknown message type"
        
        # Log usage stats
        logger.info("=" * 60)
        logger.info("📊 AGENT USAGE STATS (this session):")
        for agent_name, count in self.agent_usage_stats.items():
            status = "✅" if count > 0 else "⚪"
            logger.info(f"  {status} {agent_name}: {count} calls")
        logger.info("=" * 60)

        return response_data

    async def _apply_personality(self, chunks: list, emotion: dict) -> list:
        """Helper to pass text chunks through personality agent."""
        final_chunks = []
        for chunk in chunks:
            if chunk.get('type') == 'text':
                refined = await self.personality_agent.process({
                    "text": chunk['content'],
                    "emotion": emotion
                })
                # Assuming refined returns dict, update content
                chunk['content'] = refined.get('text', chunk['content'])
            final_chunks.append(chunk)
        return final_chunks
