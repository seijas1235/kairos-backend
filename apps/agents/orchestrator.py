"""
AI Orchestrator - Multi-Agent Coordinator for KAIROS
====================================================

Coordinates 5 specialized Gemini 3 agents + Lesson Generator:
1. EmotionAgent (Gemini 3 Flash) - Real-time emotion detection
2. ContentAdapterAgent (Gemini 3 Pro) - Intelligent content adaptation
3. LearningPathAgent (Gemini 3 Pro) - Learning path optimization
4. AssessmentAgent (Gemini 3 Pro) - Comprehension evaluation
5. PersonalityAgent (Gemini 3 Flash) - Tone personalization
6. LessonGeneratorAgent (Gemini 3 Flash) - Lesson content generation

The orchestrator decides which agent(s) to call based on the request type.
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """
    Multi-agent orchestrator that coordinates all KAIROS AI agents.
    
    Routes requests to the appropriate specialized agent(s) and combines
    their outputs for comprehensive adaptive learning.
    """
    
    def __init__(self):
        """Initialize orchestrator with all 6 agents."""
        logger.info("Initializing AI Orchestrator with Gemini 3 agents...")
        
        # Import agents
        from .ai_agents import (
            EmotionAgent,
            ContentAdapterAgent,
            LearningPathAgent,
            AssessmentAgent,
            PersonalityAgent
        )
        from .lesson_generator_agent import LessonGeneratorAgent
        
        # Initialize all agents
        self.emotion_agent = EmotionAgent()
        self.content_adapter = ContentAdapterAgent()
        self.learning_path = LearningPathAgent()
        self.assessment = AssessmentAgent()
        self.personality = PersonalityAgent()
        self.lesson_generator = LessonGeneratorAgent()
        
        logger.info("✅ All 6 agents initialized successfully")
        logger.info(f"   - EmotionAgent: {self.emotion_agent.model_name}")
        logger.info(f"   - ContentAdapterAgent: {self.content_adapter.model_name}")
        logger.info(f"   - LearningPathAgent: {self.learning_path.model_name}")
        logger.info(f"   - AssessmentAgent: {self.assessment.model_name}")
        logger.info(f"   - PersonalityAgent: {self.personality.model_name}")
        logger.info(f"   - LessonGeneratorAgent: {self.lesson_generator.model_name}")
    
    # ========================================================================
    # AGENT 1: EMOTION DETECTION (Gemini 3 Flash)
    # ========================================================================
    
    async def detect_emotion(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect student emotion from webcam frame.
        Uses EmotionAgent (Gemini 3 Flash) for fast processing.
        
        Args:
            frame_data: {
                'frame': base64 encoded image,
                'timestamp': ISO timestamp
            }
            
        Returns:
            {
                'emotion': str,
                'confidence': float,
                'attention_level': int,
                'stress_level': int,
                'timestamp': str
            }
        """
        logger.info("[Orchestrator] Routing to EmotionAgent (Gemini 3 Flash)")
        return await self.emotion_agent.process(frame_data)
    
    # ========================================================================
    # AGENT 2: CONTENT ADAPTATION (Gemini 3 Pro)
    # ========================================================================
    
    async def adapt_content(
        self,
        current_content: Dict[str, Any],
        emotion: str,
        learning_style: str = 'visual',
        topic: str = 'Unknown',
        difficulty: str = 'intermediate'
    ) -> Dict[str, Any]:
        """
        Adapt content based on student emotion.
        Uses ContentAdapterAgent (Gemini 3 Pro) for quality adaptation.
        
        Args:
            current_content: Current lesson content
            emotion: Detected emotion state
            learning_style: Student's learning style
            topic: Current topic
            difficulty: Difficulty level
            
        Returns:
            {
                'adapted_content': Dict,
                'strategy': str,
                'explanation': str,
                'confidence': float
            }
        """
        logger.info(f"[Orchestrator] Routing to ContentAdapterAgent (Gemini 3 Pro) - Emotion: {emotion}")
        
        input_data = {
            'current_content': current_content,
            'emotion': emotion,
            'learning_style': learning_style,
            'topic': topic,
            'difficulty': difficulty
        }
        
        return await self.content_adapter.process(input_data)
    
    # ========================================================================
    # AGENT 3: LEARNING PATH OPTIMIZATION (Gemini 3 Pro)
    # ========================================================================
    
    async def optimize_learning_path(
        self,
        emotion_history: List[Dict],
        completed_lessons: List[str],
        current_lesson: str,
        user_profile: Dict[str, Any],
        available_lessons: List[Dict]
    ) -> Dict[str, Any]:
        """
        Optimize learning path based on student progress and emotions.
        Uses LearningPathAgent (Gemini 3 Pro) for intelligent planning.
        
        Args:
            emotion_history: List of emotion detections
            completed_lessons: List of completed lesson IDs
            current_lesson: Current lesson ID
            user_profile: Student profile data
            available_lessons: Available next lessons
            
        Returns:
            {
                'next_lesson': Dict,
                'learning_modality': str,
                'pacing_recommendation': str,
                'estimated_time': int,
                'reasoning': str
            }
        """
        logger.info("[Orchestrator] Routing to LearningPathAgent (Gemini 3 Pro)")
        
        input_data = {
            'emotion_history': emotion_history,
            'completed_lessons': completed_lessons,
            'current_lesson': current_lesson,
            'user_profile': user_profile,
            'available_lessons': available_lessons
        }
        
        return await self.learning_path.process(input_data)
    
    # ========================================================================
    # AGENT 4: ASSESSMENT (Gemini 3 Pro)
    # ========================================================================
    
    async def assess_comprehension(
        self,
        topic: str,
        content_covered: str,
        student_responses: List[str],
        emotion_during_learning: List[Dict],
        time_spent: int
    ) -> Dict[str, Any]:
        """
        Assess student comprehension and identify knowledge gaps.
        Uses AssessmentAgent (Gemini 3 Pro) for nuanced evaluation.
        
        Args:
            topic: Topic being assessed
            content_covered: Content that was taught
            student_responses: Student's responses/interactions
            emotion_during_learning: Emotion data during learning
            time_spent: Time spent in seconds
            
        Returns:
            {
                'comprehension_score': int,
                'confidence_level': str,
                'knowledge_gaps': List[str],
                'strengths': List[str],
                'recommendations': List[str]
            }
        """
        logger.info(f"[Orchestrator] Routing to AssessmentAgent (Gemini 3 Pro) - Topic: {topic}")
        
        input_data = {
            'topic': topic,
            'content_covered': content_covered,
            'student_responses': student_responses,
            'emotion_during_learning': emotion_during_learning,
            'time_spent': time_spent
        }
        
        return await self.assessment.process(input_data)
    
    # ========================================================================
    # AGENT 5: PERSONALITY CUSTOMIZATION (Gemini 3 Flash)
    # ========================================================================
    
    async def personalize_tone(
        self,
        user_profile: Dict[str, Any],
        current_emotion: str,
        topic: str,
        difficulty: str = 'intermediate'
    ) -> Dict[str, Any]:
        """
        Generate personality parameters for teaching style.
        Uses PersonalityAgent (Gemini 3 Flash) for fast customization.
        
        Args:
            user_profile: Student profile (age, interests, preferences)
            current_emotion: Current emotional state
            topic: Current topic
            difficulty: Difficulty level
            
        Returns:
            {
                'tone': str,
                'language_complexity': str,
                'use_humor': bool,
                'use_analogies': bool,
                'analogy_domain': str,
                'pacing': str,
                'encouragement_frequency': str
            }
        """
        logger.info(f"[Orchestrator] Routing to PersonalityAgent (Gemini 3 Flash) - Emotion: {current_emotion}")
        
        input_data = {
            'user_profile': user_profile,
            'current_emotion': current_emotion,
            'topic': topic,
            'difficulty': difficulty
        }
        
        return await self.personality.process(input_data)
    
    # ========================================================================
    # LESSON GENERATION (Gemini 3 Flash)
    # ========================================================================
    
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
    
    # ========================================================================
    # ORCHESTRATION: COMPLETE LEARNING SESSION
    # ========================================================================
    
    async def process_learning_session(
        self,
        frame_data: Dict[str, Any],
        current_content: Dict[str, Any],
        user_profile: Dict[str, Any],
        topic: str,
        difficulty: str = 'intermediate'
    ) -> Dict[str, Any]:
        """
        Process a complete learning session using all agents.
        
        This is the main orchestration method that:
        1. Detects emotion (EmotionAgent)
        2. Personalizes tone (PersonalityAgent)
        3. Adapts content if needed (ContentAdapterAgent)
        
        Args:
            frame_data: Webcam frame data
            current_content: Current lesson content
            user_profile: Student profile
            topic: Current topic
            difficulty: Difficulty level
            
        Returns:
            Complete session result with emotion, personality, and adapted content
        """
        logger.info("[Orchestrator] 🎯 Processing complete learning session with all agents")
        
        # Step 1: Detect emotion (Flash - Fast)
        emotion_result = await self.detect_emotion(frame_data)
        logger.info(f"   ✓ Emotion detected: {emotion_result.get('emotion')}")
        
        # Step 2: Personalize tone (Flash - Fast)
        personality = await self.personalize_tone(
            user_profile=user_profile,
            current_emotion=emotion_result['emotion'],
            topic=topic,
            difficulty=difficulty
        )
        logger.info(f"   ✓ Personality customized: {personality.get('tone')} tone")
        
        # Step 3: Adapt content if emotion requires it (Pro - Quality)
        adaptation_result = None
        if emotion_result['emotion'] in ['confused', 'bored', 'frustrated']:
            adaptation_result = await self.adapt_content(
                current_content=current_content,
                emotion=emotion_result['emotion'],
                learning_style=user_profile.get('learning_style', 'visual'),
                topic=topic,
                difficulty=difficulty
            )
            logger.info(f"   ✓ Content adapted: {adaptation_result.get('strategy')}")
        else:
            logger.info(f"   ✓ No adaptation needed (emotion: {emotion_result['emotion']})")
        
        # Combine results
        return {
            'emotion': emotion_result,
            'personality': personality,
            'adaptation': adaptation_result,
            'action': 'adapt' if adaptation_result else 'continue',
            'timestamp': frame_data.get('timestamp')
        }
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about all active agents and their models."""
        return {
            'total_agents': 6,
            'agents': {
                'emotion_agent': {
                    'model': self.emotion_agent.model_name,
                    'type': 'EmotionAgent',
                    'gemini_version': 'Flash',
                    'purpose': 'Real-time emotion detection',
                    'status': 'active'
                },
                'content_adapter': {
                    'model': self.content_adapter.model_name,
                    'type': 'ContentAdapterAgent',
                    'gemini_version': 'Pro',
                    'purpose': 'Intelligent content adaptation',
                    'status': 'active'
                },
                'learning_path': {
                    'model': self.learning_path.model_name,
                    'type': 'LearningPathAgent',
                    'gemini_version': 'Pro',
                    'purpose': 'Learning path optimization',
                    'status': 'active'
                },
                'assessment': {
                    'model': self.assessment.model_name,
                    'type': 'AssessmentAgent',
                    'gemini_version': 'Pro',
                    'purpose': 'Comprehension evaluation',
                    'status': 'active'
                },
                'personality': {
                    'model': self.personality.model_name,
                    'type': 'PersonalityAgent',
                    'gemini_version': 'Flash',
                    'purpose': 'Tone personalization',
                    'status': 'active'
                },
                'lesson_generator': {
                    'model': self.lesson_generator.model_name,
                    'type': 'LessonGeneratorAgent',
                    'gemini_version': 'Flash',
                    'purpose': 'Lesson content generation',
                    'status': 'active'
                }
            },
            'gemini_3_compliance': True,
            'flash_agents': ['emotion_agent', 'personality', 'lesson_generator'],
            'pro_agents': ['content_adapter', 'learning_path', 'assessment']
        }
    
    # ========================================================================
    # BACKWARD COMPATIBILITY: WebSocket Consumer Methods
    # ========================================================================
    
    def __init_session_tracking(self):
        """Initialize session tracking for analytics."""
        if not hasattr(self, 'session_data'):
            self.session_data = {
                'emotion_history': [],
                'adaptations': 0,
                'total_detections': 0
            }
    
    async def process_frame(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process frame for WebSocket consumer (backward compatibility).
        
        This method wraps process_learning_session() to maintain compatibility
        with existing WebSocket consumer code.
        
        Args:
            frame_data: Frame data from WebSocket including:
                - frame: base64 image
                - timestamp: ISO timestamp
                - current_content: Current lesson content
                - user_profile: Student profile
                - topic: Current topic
                - difficulty: Difficulty level
                - block_completed: (optional) If block was completed
                - session_id: Session identifier
                
        Returns:
            Result dictionary with emotion, adaptation, and next steps
        """
        self.__init_session_tracking()
        
        # Check if this is a block completion (triggers assessment)
        if frame_data.get('block_completed'):
            return await self._process_block_completion(frame_data)
        
        # Regular frame processing
        result = await self.process_learning_session(
            frame_data={
                'frame': frame_data.get('frame'),
                'timestamp': frame_data.get('timestamp')
            },
            current_content=frame_data.get('current_content', {}),
            user_profile=frame_data.get('user_profile', {}),
            topic=frame_data.get('topic', 'Unknown'),
            difficulty=frame_data.get('difficulty', 'intermediate')
        )
        
        # Track for analytics
        self.session_data['emotion_history'].append(result['emotion'])
        self.session_data['total_detections'] += 1
        if result['action'] == 'adapt':
            self.session_data['adaptations'] += 1
        
        return result
    
    async def _process_block_completion(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process block completion with assessment and path optimization."""
        
        # Step 1: Assess comprehension
        assessment = await self.assess_comprehension(
            topic=data.get('topic', 'Unknown'),
            content_covered=data.get('content_summary', ''),
            student_responses=data.get('responses', []),
            emotion_during_learning=self.session_data.get('emotion_history', []),
            time_spent=data.get('time_spent', 0)
        )
        
        # Step 2: Optimize learning path
        next_lesson = None
        if data.get('available_lessons'):
            path_result = await self.optimize_learning_path(
                emotion_history=self.session_data.get('emotion_history', []),
                completed_lessons=data.get('completed_lessons', []),
                current_lesson=data.get('current_lesson', ''),
                user_profile=data.get('user_profile', {}),
                available_lessons=data.get('available_lessons', [])
            )
            next_lesson = path_result.get('next_lesson')
        
        return {
            'action': 'next_lesson',
            'assessment': assessment,
            'next_lesson': next_lesson,
            'timestamp': data.get('timestamp')
        }
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """
        Get session analytics (backward compatibility for WebSocket).
        
        Returns:
            Dictionary with session statistics
        """
        self.__init_session_tracking()
        
        emotion_history = self.session_data.get('emotion_history', [])
        total = len(emotion_history)
        
        if total == 0:
            return {
                'total_detections': 0,
                'total_adaptations': 0,
                'emotion_distribution': {},
                'avg_attention': 0,
                'engagement_rate': 0
            }
        
        # Count emotions
        emotion_counts = {}
        total_attention = 0
        
        for detection in emotion_history:
            emotion = detection.get('emotion', 'neutral')
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            total_attention += detection.get('attention_level', 5)
        
        # Calculate engagement rate
        engaged_count = emotion_counts.get('engaged', 0)
        engagement_rate = (engaged_count / total * 100) if total > 0 else 0
        
        return {
            'total_detections': total,
            'total_adaptations': self.session_data.get('adaptations', 0),
            'emotion_distribution': emotion_counts,
            'avg_attention': round(total_attention / total, 1) if total > 0 else 0,
            'engagement_rate': round(engagement_rate, 1)
        }
    
    def reset_session(self) -> None:
        """
        Reset session state (backward compatibility for WebSocket).
        
        Clears emotion history and analytics for a new learning session.
        """
        self.session_data = {
            'emotion_history': [],
            'adaptations': 0,
            'total_detections': 0
        }
        logger.info("[Orchestrator] Session state reset")
