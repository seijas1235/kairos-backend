"""
Assessment Agent using Gemini 3 Pro for real-time comprehension evaluation.
Assesses student understanding based on responses and emotional cues.
"""
import json
from typing import Dict, Any, List
from .base_agent import BaseAgent


class AssessmentAgent(BaseAgent):
    """
    Evaluates student comprehension and identifies knowledge gaps.
    Uses Gemini 3 Pro for nuanced assessment.
    """
    
    def __init__(self):
        """Initialize with Gemini 3 Pro for assessment quality."""
        super().__init__('gemini-3.0-pro')
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess student understanding.
        
        Args:
            input_data: {
                'topic': str,
                'content_covered': str,
                'student_responses': List[str],
                'emotion_during_learning': List[Dict],
                'time_spent': int (seconds)
            }
            
        Returns:
            {
                'comprehension_score': int (0-100),
                'confidence_level': str (low|medium|high),
                'knowledge_gaps': List[str],
                'strengths': List[str],
                'recommendations': List[str]
            }
        """
        try:
            topic = input_data.get('topic', 'Unknown')
            content = input_data.get('content_covered', '')
            responses = input_data.get('student_responses', [])
            emotions = input_data.get('emotion_during_learning', [])
            time_spent = input_data.get('time_spent', 0)
            
            # Analyze emotional state during learning
            emotion_summary = self._summarize_emotions(emotions)
            
            prompt = f"""
            You are an expert educational assessor for KAIROS.
            
            Topic: {topic}
            Content Covered: {content}
            
            Student Responses/Interactions:
            {json.dumps(responses, indent=2)}
            
            Emotional State During Learning:
            - Confusion instances: {emotion_summary['confused_count']}
            - Boredom instances: {emotion_summary['bored_count']}
            - Engaged instances: {emotion_summary['engaged_count']}
            - Average attention: {emotion_summary['avg_attention']}/10
            
            Time Spent: {time_spent} seconds
            
            Assess:
            1. Comprehension level (0-100%)
            2. Confidence in understanding (low/medium/high)
            3. Specific knowledge gaps
            4. Areas of strength
            5. Actionable recommendations
            
            Consider:
            - Quality and accuracy of responses
            - Emotional engagement patterns
            - Time efficiency
            - Depth of understanding
            
            Respond ONLY with valid JSON:
            {{
                "comprehension_score": 75,
                "confidence_level": "medium",
                "knowledge_gaps": ["specific gap 1", "specific gap 2"],
                "strengths": ["strength 1", "strength 2"],
                "recommendations": ["recommendation 1", "recommendation 2"],
                "reasoning": "Brief explanation of assessment"
            }}
            """
            
            response_text = await self.generate_content(prompt)
            
            # Parse response
            assessment = json.loads(response_text.strip())
            
            return {
                'comprehension_score': assessment.get('comprehension_score', 50),
                'confidence_level': assessment.get('confidence_level', 'medium'),
                'knowledge_gaps': assessment.get('knowledge_gaps', []),
                'strengths': assessment.get('strengths', []),
                'recommendations': assessment.get('recommendations', []),
                'reasoning': assessment.get('reasoning', ''),
                'emotion_impact': emotion_summary
            }
            
        except Exception as e:
            print(f"Error in AssessmentAgent: {e}")
            return {
                'comprehension_score': 50,
                'confidence_level': 'medium',
                'knowledge_gaps': [],
                'strengths': [],
                'recommendations': ['Continue practicing'],
                'error': str(e)
            }
    
    def _summarize_emotions(self, emotions: List[Dict]) -> Dict[str, Any]:
        """Summarize emotional state during learning."""
        if not emotions:
            return {
                'confused_count': 0,
                'bored_count': 0,
                'engaged_count': 0,
                'avg_attention': 5
            }
        
        emotion_list = [e.get('emotion', 'neutral') for e in emotions]
        attentions = [e.get('attention_level', 5) for e in emotions]
        
        return {
            'confused_count': emotion_list.count('confused'),
            'bored_count': emotion_list.count('bored'),
            'engaged_count': emotion_list.count('engaged'),
            'frustrated_count': emotion_list.count('frustrated'),
            'avg_attention': sum(attentions) / len(attentions) if attentions else 5
        }
