"""
Learning Path Optimizer Agent using Gemini 3 Pro.
Analyzes student progress and emotions to recommend optimal learning paths.
"""
import json
from typing import Dict, Any, List
from .base_agent import BaseAgent


class LearningPathAgent(BaseAgent):
    """
    Optimizes learning paths based on student performance and emotional state.
    Uses Gemini 3 Pro for intelligent path planning.
    """
    
    def __init__(self):
        """Initialize with Gemini 3 Pro for complex reasoning."""
        super().__init__('gemini-3.0-pro')
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize learning path based on student data.
        
        Args:
            input_data: {
                'emotion_history': List[Dict],
                'completed_lessons': List[str],
                'current_lesson': str,
                'user_profile': {
                    'learning_style': str,
                    'difficulty_preference': str,
                    'interests': List[str]
                },
                'available_lessons': List[Dict]
            }
            
        Returns:
            {
                'next_lesson': {
                    'id': str,
                    'title': str,
                    'difficulty': str,
                    'estimated_time': int
                },
                'learning_modality': str (visual|text|interactive),
                'pacing_recommendation': str (slower|normal|faster),
                'reasoning': str
            }
        """
        try:
            emotion_history = input_data.get('emotion_history', [])
            completed = input_data.get('completed_lessons', [])
            profile = input_data.get('user_profile', {})
            available = input_data.get('available_lessons', [])
            
            # Analyze emotional patterns
            emotion_analysis = self._analyze_emotions(emotion_history)
            
            # Build recommendation prompt
            prompt = f"""
            You are an expert learning path optimizer for KAIROS.
            
            Student Profile:
            - Learning Style: {profile.get('learning_style', 'visual')}
            - Completed Lessons: {len(completed)}
            - Recent Emotional State: {emotion_analysis['dominant_emotion']}
            - Average Attention: {emotion_analysis['avg_attention']}/10
            - Stress Level: {emotion_analysis['avg_stress']}/10
            
            Emotional Patterns:
            - Confusion Rate: {emotion_analysis['confusion_rate']}%
            - Boredom Rate: {emotion_analysis['boredom_rate']}%
            - Engagement Rate: {emotion_analysis['engagement_rate']}%
            
            Available Next Lessons:
            {json.dumps(available, indent=2)}
            
            Recommend:
            1. Best next lesson (consider difficulty, topic, and student state)
            2. Optimal learning modality (visual/text/interactive)
            3. Pacing (slower/normal/faster)
            4. Estimated time needed
            
            Respond ONLY with valid JSON:
            {{
                "next_lesson_id": "lesson_id",
                "learning_modality": "visual",
                "pacing": "normal",
                "estimated_minutes": 15,
                "reasoning": "Why this lesson is best right now"
            }}
            """
            
            response_text = await self.generate_content(prompt)
            
            # Parse response
            recommendation = json.loads(response_text.strip())
            
            # Find full lesson details
            next_lesson = next(
                (l for l in available if l['id'] == recommendation['next_lesson_id']),
                available[0] if available else None
            )
            
            return {
                'next_lesson': next_lesson,
                'learning_modality': recommendation.get('learning_modality', 'visual'),
                'pacing_recommendation': recommendation.get('pacing', 'normal'),
                'estimated_time': recommendation.get('estimated_minutes', 15),
                'reasoning': recommendation.get('reasoning', 'Optimized for current state')
            }
            
        except Exception as e:
            print(f"Error in LearningPathAgent: {e}")
            # Fallback to first available lesson
            available = input_data.get('available_lessons', [])
            return {
                'next_lesson': available[0] if available else None,
                'learning_modality': 'visual',
                'pacing_recommendation': 'normal',
                'estimated_time': 15,
                'reasoning': 'Default recommendation due to error',
                'error': str(e)
            }
    
    def _analyze_emotions(self, emotion_history: List[Dict]) -> Dict[str, Any]:
        """Analyze emotion history for patterns."""
        if not emotion_history:
            return {
                'dominant_emotion': 'neutral',
                'avg_attention': 5,
                'avg_stress': 5,
                'confusion_rate': 0,
                'boredom_rate': 0,
                'engagement_rate': 0
            }
        
        total = len(emotion_history)
        emotions = [e.get('emotion', 'neutral') for e in emotion_history]
        attentions = [e.get('attention_level', 5) for e in emotion_history]
        stresses = [e.get('stress_level', 5) for e in emotion_history]
        
        return {
            'dominant_emotion': max(set(emotions), key=emotions.count),
            'avg_attention': sum(attentions) / len(attentions),
            'avg_stress': sum(stresses) / len(stresses),
            'confusion_rate': round((emotions.count('confused') / total) * 100, 1),
            'boredom_rate': round((emotions.count('bored') / total) * 100, 1),
            'engagement_rate': round((emotions.count('engaged') / total) * 100, 1)
        }
