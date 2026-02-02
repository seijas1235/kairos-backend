"""
AI Orchestrator - Simplified multi-model coordinator for KAIROS.

Coordinates Gemini 3 models:
1. Gemini 3 Flash - Lesson generation (fast)
2. Gemini 3 Pro - Content adaptation (intelligent)
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """
    Simplified orchestrator that coordinates Gemini 3 models.
    
    Currently manages:
    - LessonGeneratorAgent (Gemini 3 Flash)
    - ContentAdapterAgent (Gemini 3 Pro) - when created
    """
    
    def __init__(self):
        """Initialize orchestrator with available agents."""
        logger.info("Initializing AI Orchestrator...")
        
        # Import here to avoid circular dependencies
        from .lesson_generator_agent import LessonGeneratorAgent
        
        self.lesson_generator = LessonGeneratorAgent()
        
        # Content adapter will be initialized when created
        self.content_adapter = None
        
        logger.info(f"AI Orchestrator initialized with Gemini 3 models")
    
    def generate_lesson(
        self,
        topic: str,
        level: str,
        learning_style: str,
        age: Optional[int] = None,
        alias: Optional[str] = None,
        language: str = "en",
        excluded_topics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate lesson using Gemini 3 Flash.
        
        Routes request to LessonGeneratorAgent which uses gemini-3-flash-preview.
        """
        logger.info(f"[Orchestrator] Generating lesson: topic='{topic}', model=Gemini 3 Flash")
        
        try:
            lesson_data = self.lesson_generator.generate_lesson(
                topic=topic,
                level=level,
                learning_style=learning_style,
                age=age,
                alias=alias,
                language=language,
                excluded_topics=excluded_topics
            )
            
            topics_count = lesson_data.get('curriculum', {}).get('total_topics', 0)
            logger.info(f"[Orchestrator] Lesson generated: {topics_count} topics created")
            
            return lesson_data
            
        except Exception as e:
            logger.error(f"[Orchestrator] Error generating lesson: {str(e)}")
            raise
    
    def adapt_content(
        self,
        original_content: str,
        emotion_state: str,
        topic: str,
        level: str,
        learning_style: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Adapt content using Gemini 3 Pro (when implemented).
        
        Currently returns original content as fallback.
        """
        logger.info(f"[Orchestrator] Content adaptation requested for emotion: {emotion_state}")
        
        if self.content_adapter is None:
            logger.warning("[Orchestrator] ContentAdapterAgent not yet implemented, using fallback")
            return {
                'adapted_content': original_content,
                'adaptation_type': 'none',
                'explanation': 'Content adapter not yet implemented'
            }
        
        try:
            adapted = self.content_adapter.adapt_content(
                original_content=original_content,
                emotion_state=emotion_state,
                topic=topic,
                level=level,
                learning_style=learning_style,
                language=language
            )
            
            logger.info(f"[Orchestrator] Content adapted successfully")
            return adapted
            
        except Exception as e:
            logger.error(f"[Orchestrator] Error adapting content: {str(e)}")
            return {
                'adapted_content': original_content,
                'adaptation_type': 'error',
                'explanation': f'Adaptation failed: {str(e)}'
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about active models."""
        info = {
            'lesson_generator': {
                'model': self.lesson_generator.model_name,
                'config': self.lesson_generator.generation_config,
                'status': 'active'
            }
        }
        
        if self.content_adapter:
            info['content_adapter'] = {
                'model': self.content_adapter.model_name,
                'config': self.content_adapter.generation_config,
                'status': 'active'
            }
        else:
            info['content_adapter'] = {
                'status': 'not_implemented'
            }
        
        return info
