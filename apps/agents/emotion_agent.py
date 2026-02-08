import json
import base64
from .base_agent import KairosAgent
from google.genai import types
import logging

logger = logging.getLogger(__name__)

class EmotionAgent(KairosAgent):
    def get_model_name(self) -> str:
        return self.MODEL_FLASH  # Use Flash for fast emotion detection

    async def process(self, input_data: dict) -> dict:
        """
        Analyzes facial expression from base64 frame using Gemini Vision (Flash).
        Returns: {emotion: str, confidence: float, action: str}
        """
        frame_base64 = input_data.get('frame', '')
        
        if not frame_base64:
            logger.warning("⚠️ [EmotionAgent] No frame provided")
            return {
                "emotion": "neutral",
                "confidence": 0.0,
                "action": "continue"
            }
        
        try:
            # Decode base64 image
            if ',' in frame_base64:
                # Remove data:image/jpeg;base64, prefix if present
                frame_base64 = frame_base64.split(',')[1]
            
            try:
                image_bytes = base64.b64decode(frame_base64)
                logger.info(f"🎭 [EmotionAgent] Frame decoded: {len(image_bytes)} bytes")
            except Exception as decode_error:
                logger.error(f"❌ [EmotionAgent] Base64 decode failed: {decode_error}")
                return {
                    "emotion": "neutral",
                    "confidence": 0.0,
                    "action": "continue",
                    "error": "decode_failed"
                }
            
            logger.info(f"🎭 [EmotionAgent] Analyzing frame ({len(image_bytes)} bytes)")
            
            # Prompt for emotion detection (EN ESPAÑOL para mejor contexto)
            prompt = """Analiza la expresión facial de este estudiante durante una sesión de aprendizaje.

Clasifica la emoción en UNA de estas categorías:
- engaged: Estudiante enfocado, interesado, ojos atentos
- confused: Estudiante muestra confusión, ceño fruncido, expresión incierta
- bored: Estudiante se ve desinteresado, distraído o cansado
- frustrated: Estudiante muestra signos de frustración o dificultad
- neutral: No se detecta emoción fuerte

Devuelve SOLO un objeto JSON con este formato exacto:
{
    "emotion": "engaged",
    "confidence": 0.85,
    "action": "continue"
}

Reglas:
- emotion: una de las 5 categorías anteriores
- confidence: número entre 0 y 1
- action: "continue" si engaged/neutral, "adapt" si confused/bored/frustrated
"""
            
            # REAL CALL TO GEMINI VISION (FLASH)
            logger.info("📡 [EmotionAgent] Calling Gemini Vision API...")
            
            response = self._generate_content(
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type='image/jpeg'
                    ),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    temperature=0.3  # Lower temperature for consistent classification
                )
            )
            
            logger.info(f"✅ [EmotionAgent] API response received")
            
            # Validate response
            if not response or not response.text:
                logger.warning("⚠️ [EmotionAgent] Empty response from Gemini Vision (possibly blocked)")
                return {
                    "emotion": "neutral",
                    "confidence": 0.5,
                    "action": "continue"
                }
            
            # Parse JSON response
            raw_text = response.text.strip()
            logger.debug(f"📝 [EmotionAgent] Raw response: {raw_text[:200]}")
            
            # Clean markdown if present
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text.replace("```", "").strip()
            
            result = json.loads(raw_text)
            logger.debug(f"📊 [EmotionAgent] Parsed JSON: {result}")
            
            # Validate response structure
            emotion = result.get('emotion', 'neutral')
            confidence = result.get('confidence', 0.0)
            action = result.get('action', 'continue')
            
            logger.info(f"✅ [EmotionAgent] Detected: {emotion} ({confidence*100:.0f}%) → {action}")
            
            return {
                "emotion": emotion,
                "confidence": float(confidence),
                "action": action
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ [EmotionAgent] JSON parsing error: {e}")
            if 'raw_text' in locals():
                logger.error(f"📄 [EmotionAgent] Raw response was: {raw_text}")
            return {
                "emotion": "neutral",
                "confidence": 0.0,
                "action": "continue",
                "error": "json_parse_failed"
            }
            
        except Exception as e:
            logger.error(f"❌ [EmotionAgent] Error analyzing frame: {e}", exc_info=True)
            return {
                "emotion": "neutral",
                "confidence": 0.0,
                "action": "continue",
                "error": str(e)
            }
