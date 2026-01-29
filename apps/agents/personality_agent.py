"""
Personality Tutor Agent using Gemini 3 Flash for personalized teaching style.
Adapts tone, language complexity, and teaching approach to student preferences.
"""
import json
from typing import Dict, Any
from .base_agent import BaseAgent


class PersonalityAgent(BaseAgent):
    """
    Personalizes teaching tone and style based on student profile and emotional state.
    Uses Gemini 3 Flash for quick personality adjustments.
    """
    
    def __init__(self):
        """Initialize with Gemini 3 Flash for fast style adaptation."""
        super().__init__('gemini-3.0-flash')
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized teaching style parameters.
        
        Args:
            input_data: {
                'user_profile': {
                    'age': int,
                    'interests': List[str],
                    'preferred_tone': str
                },
                'current_emotion': str,
                'topic': str,
                'difficulty': str
            }
            
        Returns:
            {
                'tone': str (encouraging|neutral|challenging|playful),
                'language_complexity': str (simple|moderate|advanced),
                'use_humor': bool,
                'use_analogies': bool,
                'analogy_domain': str (sports|games|movies|etc),
                'pacing': str (slow|moderate|fast),
                'encouragement_frequency': str (high|medium|low)
            }
        """
        try:
            profile = input_data.get('user_profile', {})
            emotion = input_data.get('current_emotion', 'neutral')
            topic = input_data.get('topic', 'Unknown')
            difficulty = input_data.get('difficulty', 'intermediate')
            
            prompt = f"""
            You are a personality customization expert for KAIROS AI tutor.
            
            Student Profile:
            - Age: {profile.get('age', 'unknown')}
            - Interests: {', '.join(profile.get('interests', ['general']))}
            - Preferred Tone: {profile.get('preferred_tone', 'encouraging')}
            
            Current Context:
            - Emotion: {emotion}
            - Topic: {topic}
            - Difficulty: {difficulty}
            
            Determine the optimal teaching personality:
            1. Tone (encouraging/neutral/challenging/playful)
            2. Language complexity (simple/moderate/advanced)
            3. Whether to use humor
            4. Whether to use analogies (and from which domain)
            5. Pacing (slow/moderate/fast)
            6. How often to provide encouragement
            
            Guidelines:
            - If confused/frustrated: More encouraging, simpler language
            - If bored: More playful, use humor and challenges
            - If engaged: Can be more challenging and complex
            - Match analogies to student interests
            
            Respond ONLY with valid JSON:
            {{
                "tone": "encouraging",
                "language_complexity": "moderate",
                "use_humor": true,
                "use_analogies": true,
                "analogy_domain": "video games",
                "pacing": "moderate",
                "encouragement_frequency": "medium",
                "example_phrase": "Example of how to speak in this style"
            }}
            """
            
            response_text = await self.generate_content(
                prompt,
                temperature=0.8  # Higher temperature for more personality variety
            )
            
            # Parse response
            personality = json.loads(response_text.strip())
            
            return {
                'tone': personality.get('tone', 'encouraging'),
                'language_complexity': personality.get('language_complexity', 'moderate'),
                'use_humor': personality.get('use_humor', False),
                'use_analogies': personality.get('use_analogies', True),
                'analogy_domain': personality.get('analogy_domain', 'general'),
                'pacing': personality.get('pacing', 'moderate'),
                'encouragement_frequency': personality.get('encouragement_frequency', 'medium'),
                'example_phrase': personality.get('example_phrase', '')
            }
            
        except Exception as e:
            print(f"Error in PersonalityAgent: {e}")
            return {
                'tone': 'encouraging',
                'language_complexity': 'moderate',
                'use_humor': False,
                'use_analogies': True,
                'analogy_domain': 'general',
                'pacing': 'moderate',
                'encouragement_frequency': 'medium',
                'error': str(e)
            }
    
    async def generate_personalized_message(self, message: str, personality: Dict[str, Any]) -> str:
        """
        Transform a generic message into a personalized one.
        
        Args:
            message: Generic message
            personality: Personality parameters from process()
            
        Returns:
            Personalized message
        """
        try:
            prompt = f"""
            Transform this message to match the specified teaching personality:
            
            Original Message: {message}
            
            Personality Style:
            - Tone: {personality.get('tone', 'encouraging')}
            - Language: {personality.get('language_complexity', 'moderate')}
            - Use Humor: {personality.get('use_humor', False)}
            - Use Analogies: {personality.get('use_analogies', False)}
            - Analogy Domain: {personality.get('analogy_domain', 'general')}
            
            Respond with ONLY the transformed message, no explanation.
            """
            
            return await self.generate_content(prompt, temperature=0.9)
            
        except Exception as e:
            print(f"Error generating personalized message: {e}")
            return message
