import json
from .base_agent import KairosAgent
from google.genai import types
import logging

logger = logging.getLogger(__name__)

class AssessmentAgent(KairosAgent):
    def get_model_name(self) -> str:
        return self.MODEL_PRO

    async def process(self, input_data: dict) -> dict:
        """
        Evaluates user understanding based on session data.
        Input: {topics_covered, questions_asked, duration}
        Output: {score, knowledge_gaps, recommendations}
        """
        topics = input_data.get('topics_covered', [])
        questions = input_data.get('questions_asked', [])
        duration = input_data.get('duration', 0)
        
        logger.info(f"📊 [Assessment] Evaluating session: {len(topics)} topics, {len(questions)} questions")
        
        prompt = f"""Analyze this learning session and provide an assessment.

TOPICS COVERED: {', '.join(topics) if topics else 'General content'}
USER QUESTIONS: {len(questions)} questions asked
SESSION DURATION: {duration} minutes

Based on this data, provide:
- Comprehension score (0-100)
- Identified knowledge gaps
- Specific recommendations for improvement
- Suggested next topics

Return JSON:
{{
    "score": 75,
    "knowledge_gaps": ["topic1", "topic2"],
    "recommendations": ["recommendation1", "recommendation2"],
    "next_topics": ["next1", "next2"]
}}
"""
        
        try:
            # REAL CALL TO GEMINI PRO
            response = self._generate_content(
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    temperature=0.5
                )
            )
            
            # Validate response
            if not response or not response.text:
                logger.error("❌ [Assessment] Empty response from Gemini API")
                raise ValueError("Empty response from API")
            
            raw_text = response.text.strip()
            
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(raw_text)
            
            logger.info(f"✅ [Assessment] Score: {result.get('score', 'N/A')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ [Assessment] Error: {e}", exc_info=True)
            return {
                "score": None,
                "knowledge_gaps": [],
                "recommendations": ["Continuar practicando"],
                "next_topics": []
            }

    async def generate_summary(self, session_context: dict) -> dict:
        """
        Generates final lesson summary using Gemini Pro.
        Returns: {type: 'lesson_summary', stats: {...}, pedagogical_suggestion: ...}
        """
        logger.info("📝 [Assessment] Generating lesson summary")
        
        # Extract session data
        emotions = session_context.get('emotions', [])
        topics = session_context.get('topics_covered', [])
        duration = session_context.get('duration', 0)
        
        # Count emotions
        emotion_counts = {}
        for e in emotions:
            emotion = e.get('emotion', 'neutral')
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        prompt = f"""Generate a comprehensive lesson summary.

SESSION DATA:
- Topics covered: {', '.join(topics) if topics else 'General content'}
- Duration: {duration} minutes
- Emotional states detected: {emotion_counts}

Provide:
- Key statistics
- Pedagogical insights about the student's learning style
- Actionable suggestions for future lessons

Return JSON:
{{
    "type": "lesson_summary",
    "stats": {{
        "emotions": {emotion_counts},
        "topics_covered": {topics},
        "duration": {duration}
    }},
    "pedagogical_suggestion": "Detailed insight about student's learning patterns and preferences"
}}
"""
        
        try:
            response = self._generate_content(
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    temperature=0.6
                )
            )
            
            # Validate response
            if not response or not response.text:
                logger.error("❌ [Assessment] Empty response from Gemini API (summary)")
                raise ValueError("Empty response from API")
            
            raw_text = response.text.strip()
            
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(raw_text)
            
            logger.info("✅ [Assessment] Summary generated")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ [Assessment] Error generating summary: {e}", exc_info=True)
            
            # Fallback
            return {
                "type": "lesson_summary",
                "stats": {
                    "emotions": emotion_counts,
                    "topics_covered": topics,
                    "duration": duration
                },
                "pedagogical_suggestion": "Sesión completada. Buen trabajo."
            }
