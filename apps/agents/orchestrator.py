"""
Agent Orchestrator - The brain of KAIROS multi-agent system.
Coordinates all 5 agents to provide adaptive learning experience.
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from .emotion_agent import EmotionAgent
from .content_adapter_agent import ContentAdapterAgent
from .learning_path_agent import LearningPathAgent
from .assessment_agent import AssessmentAgent
from .personality_agent import PersonalityAgent


class AgentOrchestrator:
    """
    Orchestrates multiple AI agents to create adaptive learning experience.
    
    Agents:
    1. EmotionAgent (Gemini 3 Flash) - Detects emotions
    2. ContentAdapterAgent (Gemini 3 Pro) - Adapts content
    3. LearningPathAgent (Gemini 3 Pro) - Optimizes learning path
    4. AssessmentAgent (Gemini 3 Pro) - Evaluates comprehension
    5. PersonalityAgent (Gemini 3 Flash) - Personalizes tone
    """
    
    def __init__(self):
        """Initialize all agents."""
        self.emotion_agent = EmotionAgent()
        self.content_agent = ContentAdapterAgent()
        self.path_agent = LearningPathAgent()
        self.assessment_agent = AssessmentAgent()
        self.personality_agent = PersonalityAgent()
        
        # Session state
        self.emotion_history: List[Dict] = []
        self.adaptation_history: List[Dict] = []
        self.last_adaptation_time: Optional[datetime] = None
        
        # Configuration
        self.adaptation_cooldown = 10  # seconds between adaptations
        self.emotion_threshold = 3  # consecutive negative emotions before adapting
    
    async def process_frame(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single video frame and determine actions.
        Called every 3 seconds during learning session.
        
        Args:
            session_data: {
                'frame': base64 image,
                'timestamp': ISO timestamp,
                'current_content': Dict,
                'user_profile': Dict,
                'topic': str,
                'session_id': str
            }
            
        Returns:
            {
                'action': str (continue|adapt|assess|next_lesson),
                'emotion': Dict,
                'adapted_content': Dict (if action=adapt),
                'assessment': Dict (if action=assess),
                'next_lesson': Dict (if action=next_lesson)
            }
        """
        try:
            # 1. ALWAYS detect emotion
            emotion_result = await self.emotion_agent.process({
                'frame': session_data['frame'],
                'timestamp': session_data['timestamp']
            })
            
            # Store emotion history
            self.emotion_history.append(emotion_result)
            
            # 2. Check if we need to adapt content
            if self._should_adapt_content(emotion_result):
                return await self._adapt_content(session_data, emotion_result)
            
            # 3. Check if block is completed (for assessment)
            if session_data.get('block_completed', False):
                return await self._assess_and_recommend(session_data, emotion_result)
            
            # 4. Default: continue with current content
            return {
                'action': 'continue',
                'emotion': emotion_result,
                'message': 'Continuing with current content'
            }
            
        except Exception as e:
            print(f"Error in orchestrator: {e}")
            return {
                'action': 'error',
                'error': str(e),
                'emotion': {'emotion': 'neutral', 'confidence': 0.0}
            }
    
    async def _adapt_content(self, session_data: Dict, emotion: Dict) -> Dict[str, Any]:
        """
        Adapt content based on detected emotion.
        Uses ContentAdapterAgent and PersonalityAgent.
        """
        try:
            # Get personality style
            personality = await self.personality_agent.process({
                'user_profile': session_data.get('user_profile', {}),
                'current_emotion': emotion['emotion'],
                'topic': session_data.get('topic', ''),
                'difficulty': session_data.get('difficulty', 'intermediate')
            })
            
            # Adapt content
            adapted = await self.content_agent.process({
                'current_content': session_data['current_content'],
                'emotion': emotion['emotion'],
                'learning_style': session_data.get('user_profile', {}).get('learning_style', 'visual'),
                'topic': session_data.get('topic', ''),
                'difficulty': session_data.get('difficulty', 'intermediate')
            })
            
            # Record adaptation
            adaptation_event = {
                'timestamp': datetime.now().isoformat(),
                'emotion': emotion['emotion'],
                'strategy': adapted['strategy'],
                'explanation': adapted['explanation'],
                'personality': personality
            }
            self.adaptation_history.append(adaptation_event)
            self.last_adaptation_time = datetime.now()
            
            return {
                'action': 'adapt',
                'emotion': emotion,
                'adapted_content': adapted['adapted_content'],
                'strategy': adapted['strategy'],
                'explanation': adapted['explanation'],
                'personality': personality,
                'adaptation_history': self.adaptation_history[-5:]  # Last 5 adaptations
            }
            
        except Exception as e:
            print(f"Error adapting content: {e}")
            return {
                'action': 'continue',
                'emotion': emotion,
                'error': str(e)
            }
    
    async def _assess_and_recommend(self, session_data: Dict, emotion: Dict) -> Dict[str, Any]:
        """
        Assess comprehension and recommend next lesson.
        Uses AssessmentAgent and LearningPathAgent.
        """
        try:
            # Assess current lesson
            assessment = await self.assessment_agent.process({
                'topic': session_data.get('topic', ''),
                'content_covered': session_data.get('content_summary', ''),
                'student_responses': session_data.get('responses', []),
                'emotion_during_learning': self.emotion_history,
                'time_spent': session_data.get('time_spent', 0)
            })
            
            # Recommend next lesson
            next_lesson = await self.path_agent.process({
                'emotion_history': self.emotion_history,
                'completed_lessons': session_data.get('completed_lessons', []),
                'current_lesson': session_data.get('current_lesson', ''),
                'user_profile': session_data.get('user_profile', {}),
                'available_lessons': session_data.get('available_lessons', [])
            })
            
            # Clear emotion history for next lesson
            self.emotion_history = []
            self.adaptation_history = []
            
            return {
                'action': 'next_lesson',
                'emotion': emotion,
                'assessment': assessment,
                'next_lesson': next_lesson['next_lesson'],
                'learning_modality': next_lesson['learning_modality'],
                'pacing': next_lesson['pacing_recommendation'],
                'reasoning': next_lesson['reasoning']
            }
            
        except Exception as e:
            print(f"Error in assessment: {e}")
            return {
                'action': 'continue',
                'emotion': emotion,
                'error': str(e)
            }
    
    def _should_adapt_content(self, emotion: Dict) -> bool:
        """
        Determine if content should be adapted based on emotion.
        
        Rules:
        1. Don't adapt if recently adapted (cooldown)
        2. Adapt if negative emotion persists
        3. Adapt if attention/stress levels are concerning
        """
        # Check cooldown
        if self.last_adaptation_time:
            seconds_since_last = (datetime.now() - self.last_adaptation_time).total_seconds()
            if seconds_since_last < self.adaptation_cooldown:
                return False
        
        # Check for negative emotions
        negative_emotions = ['confused', 'bored', 'frustrated']
        if emotion['emotion'] in negative_emotions:
            # Check if emotion persists
            recent_emotions = self.emotion_history[-self.emotion_threshold:]
            if len(recent_emotions) >= self.emotion_threshold:
                negative_count = sum(
                    1 for e in recent_emotions 
                    if e.get('emotion') in negative_emotions
                )
                if negative_count >= self.emotion_threshold:
                    return True
        
        # Check attention/stress levels
        attention = emotion.get('attention_level', 5)
        stress = emotion.get('stress_level', 5)
        
        if attention < 4 or stress > 7:
            return True
        
        return False
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """
        Get analytics for current session.
        
        Returns:
            Summary of emotions, adaptations, and engagement metrics
        """
        if not self.emotion_history:
            return {'status': 'no_data'}
        
        emotions = [e.get('emotion', 'neutral') for e in self.emotion_history]
        attentions = [e.get('attention_level', 5) for e in self.emotion_history]
        stresses = [e.get('stress_level', 5) for e in self.emotion_history]
        
        return {
            'total_detections': len(self.emotion_history),
            'total_adaptations': len(self.adaptation_history),
            'emotion_distribution': {
                'engaged': emotions.count('engaged'),
                'confused': emotions.count('confused'),
                'bored': emotions.count('bored'),
                'frustrated': emotions.count('frustrated'),
                'neutral': emotions.count('neutral')
            },
            'avg_attention': sum(attentions) / len(attentions),
            'avg_stress': sum(stresses) / len(stresses),
            'engagement_rate': round((emotions.count('engaged') / len(emotions)) * 100, 1),
            'adaptation_strategies_used': [a['strategy'] for a in self.adaptation_history]
        }
    
    def reset_session(self):
        """Reset session state for new learning session."""
        self.emotion_history = []
        self.adaptation_history = []
        self.last_adaptation_time = None
