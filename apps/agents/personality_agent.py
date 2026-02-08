import json
from .base_agent import KairosAgent
from google.genai import types
import logging

logger = logging.getLogger(__name__)

class PersonalityAgent(KairosAgent):
    def get_model_name(self) -> str:
        return self.MODEL_FLASH  # Fast refinement

    async def process(self, input_data: dict) -> dict:
        """
        Refines text to add warmth, empathy, and match user emotion.
        Input: {text, emotion, language, age, user_alias}
        Output: {text: refined_text}
        """
        text = input_data.get('text', '')
        emotion = input_data.get('emotion', {}).get('emotion', 'neutral')
        language = input_data.get('language', 'es')
        age = input_data.get('age', 15)
        user_alias = input_data.get('user_alias', 'Estudiante')
        
        if not text:
            return {"text": text}
        
        logger.info(f"🎨 [Personality] Refining text for: {user_alias} (age {age}, lang {language}, emotion: {emotion})")
        
        # Emotion-specific tone guidance
        tone_guidance = {
            'confused': 'Use a patient, encouraging tone. Simplify language. Add reassurance.',
            'bored': 'Use an enthusiastic, engaging tone. Add energy and interesting hooks.',
            'frustrated': 'Use a calm, supportive tone. Acknowledge difficulty. Encourage progress.',
            'engaged': 'Use an encouraging tone. Maintain momentum. Add depth.',
            'neutral': 'Use a friendly, warm tone. Be conversational and approachable.'
        }
        
        tone = tone_guidance.get(emotion, tone_guidance['neutral'])
        
        # Language instruction
        language_map = {
            'es': 'español',
            'en': 'English',
            'pt': 'português',
            'fr': 'français'
        }
        target_language = language_map.get(language, 'español')
        
        prompt = f"""You are a personality refinement agent for an adaptive tutor.

STUDENT: {user_alias}, {age} years old
LANGUAGE: Respond in {target_language}. Keep the same language as the original text.

ORIGINAL TEXT:
\"\"\"
{text}
\"\"\"

STUDENT EMOTION: {emotion}
TONE GUIDANCE: {tone}

REFINE the text to:
- Add warmth and empathy
- Match the appropriate tone for the student's emotion
- Keep the same factual content
- Make it more conversational and human
- Address the student naturally (you can use their alias: {user_alias})
- Maintain the same language as the original text
- Stay concise (similar length to original)

Return ONLY the refined text, no JSON, no markdown, no explanations.
"""
        
        try:
            # REAL CALL TO GEMINI FLASH
            response = self._generate_content(
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8  # Higher for more personality
                )
            )
            
            # Validate response
            if not response or not response.text:
                logger.warning("⚠️ [Personality] Empty response from Gemini, returning original text")
                return {"text": text}
            
            refined_text = response.text.strip()
            
            # Remove quotes if LLM added them
            if refined_text.startswith('"') and refined_text.endswith('"'):
                refined_text = refined_text[1:-1]
            
            logger.info(f"✅ [Personality] Refined text ({len(text)} → {len(refined_text)} chars)")
            
            return {"text": refined_text}
            
        except Exception as e:
            logger.error(f"❌ [Personality] Error: {e}", exc_info=True)
            # Fallback: return original
            return {"text": text}
