import json
from .base_agent import KairosAgent
from google.genai import types
import logging

logger = logging.getLogger(__name__)

class LearningPathAgent(KairosAgent):
    def get_model_name(self) -> str:
        return self.MODEL_PRO

    async def process(self, input_data: dict) -> dict:
        """
        Generates lesson structure and learning path using Gemini Pro.
        Input: {topic, style, level, language, age, user_alias}
        Output: {lesson_id, structure, estimated_duration}
        """
        topic = input_data.get('topic', 'General Topic')
        style = input_data.get('style', 'Mixto')
        level = input_data.get('level', 'intermediate')
        language = input_data.get('language', 'es')
        age = input_data.get('age', 15)
        user_alias = input_data.get('user_alias', 'Estudiante')
        
        logger.info(f"🗺️ [LearningPath] Generating path for: {topic}")
        logger.info(f"   Level: {level} | Student: {user_alias} (age {age}) | Language: {language}")
        
        # Language instruction
        language_map = {
            'es': 'español',
            'en': 'English',
            'pt': 'português',
            'fr': 'français'
        }
        target_language = language_map.get(language, 'español')
        
        prompt = f"""Design an educational lesson structure for teaching: {topic}

LANGUAGE: Respond in {target_language}. All content must be in {target_language}.

STUDENT PROFILE:
- Alias: {user_alias}
- Age: {age} years old
- Learning Level: {level}
- Learning Style: {style}

Create a structured lesson plan with:
- Clear introduction
- 2-3 main sections with specific learning objectives
- Estimated time for each section
- Brief assessment approach

Return a JSON object with this structure:
{{
    "lesson_id": "unique-id",
    "topic": "{topic}",
    "estimated_duration": "15-20 min",
    "structure": {{
        "intro": "Brief welcoming introduction text",
        "sections": [
            {{
                "title": "Section title",
                "objectives": ["objective 1", "objective 2"],
                "estimated_time": "5 min"
            }}
        ],
        "assessment": {{
            "type": "conceptual",
            "questions_count": 3
        }}
    }}
}}
"""
        
        try:
            # REAL CALL TO GEMINI PRO
            response = self._generate_content(
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    temperature=0.6
                )
            )
            
            # Validate response
            if not response or not response.text:
                logger.error("❌ [LearningPath] Empty response from Gemini API")
                raise ValueError("Empty response from API")
            
            raw_text = response.text.strip()
            
            # Clean markdown
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(raw_text)
            
            logger.info(f"✅ [LearningPath] Generated structure with {len(result.get('structure', {}).get('sections', []))} sections")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ [LearningPath] Error: {e}", exc_info=True)
            
            # Fallback
            return {
                "lesson_id": "fallback",
                "topic": topic,
                "estimated_duration": "10 min",
                "structure": {
                    "intro": f"Introducción a {topic}",
                    "sections": [
                        {
                            "title": "Conceptos básicos",
                            "objectives": ["Entender fundamentos"],
                            "estimated_time": "5 min"
                        }
                    ],
                    "assessment": {"type": "conceptual", "questions_count": 2}
                }
            }
