"""
Emotion Detection Agent using Gemini 3 Flash for real-time emotion analysis.
Uses computer vision to detect student emotions from webcam frames.
"""
import json
import base64
from typing import Dict, Any
from .base_agent import BaseAgent


class EmotionAgent(BaseAgent):
    """
    Detects student emotions from facial expressions using Gemini 3 Flash.
    Optimized for speed (3-second intervals).
    """
    
    def __init__(self):
        """Initialize with Gemini 3 Flash for fast processing."""
        super().__init__('gemini-3.0-flash')
        self.emotion_states = ['engaged', 'confused', 'bored', 'frustrated', 'neutral']
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze facial expression and detect emotion.
        
        Args:
            input_data: {
                'frame': base64 encoded image,
                'timestamp': ISO timestamp
            }
            
        Returns:
            {
                'emotion': str (engaged|confused|bored|frustrated|neutral),
                'confidence': float (0-1),
                'attention_level': int (1-10),
                'stress_level': int (1-10),
                'timestamp': str
            }
        """
        try:
            frame_data = base64.b64decode(input_data['frame'])
            
            prompt = f"""
            Analyze this student's facial expression during a learning session.
            
            Determine:
            1. Primary emotion: {', '.join(self.emotion_states)}
            2. Confidence level (0-1)
            3. Attention level (1-10, where 10 is highly focused)
            4. Stress level (1-10, where 10 is very stressed)
            
            Consider:
            - Eye contact and gaze direction
            - Facial muscle tension
            - Posture (if visible)
            - Overall engagement cues
            
            Respond ONLY with valid JSON in this exact format:
            {{
                "emotion": "engaged",
                "confidence": 0.85,
                "attention_level": 8,
                "stress_level": 3
            }}
            """
            
            response_text = await self.generate_content_with_image(
                prompt,
                frame_data,
                temperature=0.3  # Lower temperature for more consistent results
            )
            
            # Parse JSON response
            result = json.loads(response_text.strip())
            
            # Add timestamp
            result['timestamp'] = input_data.get('timestamp')
            
            # Validate emotion state
            if result['emotion'] not in self.emotion_states:
                result['emotion'] = 'neutral'
            
            return result
            
        except Exception as e:
            print(f"Error in EmotionAgent: {e}")
            return {
                'emotion': 'neutral',
                'confidence': 0.0,
                'attention_level': 5,
                'stress_level': 5,
                'timestamp': input_data.get('timestamp'),
                'error': str(e)
            }
    
    async def analyze_emotion_trend(self, emotion_history: list) -> Dict[str, Any]:
        """
        Analyze emotion trends over time.
        
        Args:
            emotion_history: List of emotion detections
            
        Returns:
            Trend analysis and recommendations
        """
        if not emotion_history:
            return {'trend': 'stable', 'recommendation': 'continue'}
        
        # Count recent emotions (last 10)
        recent = emotion_history[-10:]
        emotion_counts = {}
        for detection in recent:
            emotion = detection.get('emotion', 'neutral')
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Determine dominant emotion
        dominant = max(emotion_counts, key=emotion_counts.get)
        
        # Generate recommendation
        if dominant in ['confused', 'frustrated']:
            if emotion_counts[dominant] >= 5:
                return {
                    'trend': 'declining',
                    'dominant_emotion': dominant,
                    'recommendation': 'adapt_content',
                    'urgency': 'high'
                }
        elif dominant == 'bored':
            if emotion_counts[dominant] >= 4:
                return {
                    'trend': 'disengaging',
                    'dominant_emotion': dominant,
                    'recommendation': 'add_interactivity',
                    'urgency': 'medium'
                }
        
        return {
            'trend': 'stable',
            'dominant_emotion': dominant,
            'recommendation': 'continue',
            'urgency': 'low'
        }
