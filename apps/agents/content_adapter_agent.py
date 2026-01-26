"""
Content Adapter Agent using Gemini 3 Pro for intelligent content adaptation.
Transforms learning content based on detected emotions and learning styles.
"""
import json
from typing import Dict, Any, List
from .base_agent import BaseAgent


class ContentAdapterAgent(BaseAgent):
    """
    Adapts learning content based on student emotions and learning preferences.
    Uses Gemini 3 Pro for high-quality content generation.
    """
    
    def __init__(self):
        """Initialize with Gemini 3 Pro for quality content generation."""
        super().__init__('gemini-3.0-pro')
        
        self.adaptation_strategies = {
            'confused': 'visual_explanation',
            'bored': 'gamification',
            'frustrated': 'simplification',
            'neutral': 'maintain',
            'engaged': 'challenge'
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt content based on student emotion and context.
        
        Args:
            input_data: {
                'current_content': {
                    'title': str,
                    'body': str,
                    'type': str
                },
                'emotion': str,
                'learning_style': str (visual|auditory|kinesthetic),
                'topic': str,
                'difficulty': str
            }
            
        Returns:
            {
                'adapted_content': {
                    'title': str,
                    'body': str,
                    'type': str,
                    'imageUrl': str (optional),
                    'interactive_elements': list (optional)
                },
                'strategy': str,
                'explanation': str,
                'confidence': float
            }
        """
        try:
            current_content = input_data['current_content']
            emotion = input_data['emotion']
            learning_style = input_data.get('learning_style', 'visual')
            topic = input_data.get('topic', 'Unknown')
            
            strategy = self.adaptation_strategies.get(emotion, 'maintain')
            
            if strategy == 'maintain':
                return {
                    'adapted_content': current_content,
                    'strategy': 'maintain',
                    'explanation': 'Student is engaged, continuing with current approach',
                    'confidence': 1.0
                }
            
            # Generate adapted content
            prompt = self._build_adaptation_prompt(
                current_content,
                emotion,
                strategy,
                learning_style,
                topic
            )
            
            response_text = await self.generate_content(prompt)
            
            # Parse response
            adapted = self._parse_adapted_content(response_text, strategy)
            
            return {
                'adapted_content': adapted,
                'strategy': strategy,
                'explanation': self._get_strategy_explanation(emotion, strategy),
                'confidence': 0.85
            }
            
        except Exception as e:
            print(f"Error in ContentAdapterAgent: {e}")
            return {
                'adapted_content': input_data.get('current_content', {}),
                'strategy': 'error',
                'explanation': f'Failed to adapt content: {str(e)}',
                'confidence': 0.0
            }
    
    def _build_adaptation_prompt(self, content: Dict, emotion: str, strategy: str, 
                                 learning_style: str, topic: str) -> str:
        """Build prompt for content adaptation."""
        
        base_prompt = f"""
        You are an expert educational content adapter for KAIROS, an AI tutor.
        
        Current Situation:
        - Topic: {topic}
        - Student Emotion: {emotion}
        - Learning Style: {learning_style}
        - Current Content: {content.get('body', '')}
        
        Adaptation Strategy: {strategy}
        """
        
        if strategy == 'visual_explanation':
            return base_prompt + """
            
            The student is confused. Transform this content to be more visual and concrete:
            1. Use analogies and metaphors
            2. Describe visual diagrams or illustrations
            3. Break down complex concepts into simple steps
            4. Add real-world examples
            
            Respond with JSON:
            {
                "title": "Clear, engaging title",
                "body": "Visual explanation with analogies and examples",
                "type": "visual",
                "suggested_image": "Description of helpful diagram/illustration"
            }
            """
        
        elif strategy == 'gamification':
            return base_prompt + """
            
            The student is bored. Make this content interactive and game-like:
            1. Add a challenge or puzzle
            2. Include interactive elements
            3. Make it competitive or achievement-based
            4. Add immediate feedback mechanisms
            
            Respond with JSON:
            {
                "title": "Engaging, challenge-based title",
                "body": "Interactive explanation with game elements",
                "type": "interactive",
                "game_type": "quiz|puzzle|challenge",
                "points_possible": 100
            }
            """
        
        elif strategy == 'simplification':
            return base_prompt + """
            
            The student is frustrated. Simplify and encourage:
            1. Break into smaller, manageable chunks
            2. Use everyday language
            3. Add encouraging messages
            4. Suggest a brief mental break if needed
            5. Relate to familiar concepts
            
            Respond with JSON:
            {
                "title": "Simple, encouraging title",
                "body": "Simplified explanation with encouragement",
                "type": "text",
                "encouragement": "Motivational message",
                "break_suggestion": true/false
            }
            """
        
        elif strategy == 'challenge':
            return base_prompt + """
            
            The student is highly engaged. Provide advanced content:
            1. Add depth and complexity
            2. Introduce advanced concepts
            3. Pose thought-provoking questions
            4. Connect to broader applications
            
            Respond with JSON:
            {
                "title": "Advanced, thought-provoking title",
                "body": "Deeper explanation with advanced concepts",
                "type": "text",
                "extension_topics": ["topic1", "topic2"]
            }
            """
        
        return base_prompt
    
    def _parse_adapted_content(self, response: str, strategy: str) -> Dict[str, Any]:
        """Parse Gemini response into structured content."""
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]
            return json.loads(json_str)
        except:
            # Fallback if JSON parsing fails
            return {
                'title': 'Adapted Content',
                'body': response,
                'type': 'text'
            }
    
    def _get_strategy_explanation(self, emotion: str, strategy: str) -> str:
        """Get human-readable explanation of adaptation strategy."""
        explanations = {
            'visual_explanation': f"Detected {emotion}. Switching to visual explanation with analogies.",
            'gamification': f"Detected {emotion}. Adding interactive game elements to re-engage.",
            'simplification': f"Detected {emotion}. Simplifying content and adding encouragement.",
            'challenge': f"Student is highly engaged. Providing more advanced content."
        }
        return explanations.get(strategy, f"Adapting content based on {emotion} emotion.")
