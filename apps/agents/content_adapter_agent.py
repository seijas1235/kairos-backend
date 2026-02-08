import json
import hashlib
from .base_agent import KairosAgent
from google.genai import types
import logging

logger = logging.getLogger(__name__)

class ContentAdapterAgent(KairosAgent):
    def get_model_name(self) -> str:
        return self.MODEL_PRO

    def _generate_image_url(self, prompt: str, index: int = 0) -> str:
        """
        Generate image URL. Uses picsum.photos for reliable placeholder images.
        """
        # Use picsum.photos which provides real images (no CORS issues)
        # Alternative: Generate with Gemini Imagen 3 in production
        
        # Use a seed based on the prompt for consistent images
        import hashlib
        seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16) % 1000 + index
        
        return f"https://picsum.photos/seed/{seed}/800/500"

    async def process(self, input_data: dict) -> list:
        """
        Generates content based on user input, emotion, and style using Gemini Pro.
        Returns a LIST of JSON chunks with IMAGE URLS included.
        
        Each image_prompt chunk MUST include:
        - type: "image_prompt"
        - content: Text description (the prompt)
        - image_url: URL of the actual image to display
        - alt_text: Accessibility text
        """
        user_input = input_data.get("user_input", "")
        detected_emotion = input_data.get("detected_emotion", {})
        learning_style = input_data.get("style", "Visual")
        language = input_data.get("language", "es")  # Frontend sends language code
        age = input_data.get("age", 15)  # Frontend sends user age
        user_alias = input_data.get("user_alias", "Estudiante")
        
        logger.info(f"📝 [ContentAdapter] Processing: '{user_input[:50]}...'")
        logger.info(f"   Style: {learning_style} | Language: {language} | Age: {age}")

        # Build style-specific instructions
        style_instructions = self._get_style_instructions(learning_style)
        
        # Build emotion adaptation context
        emotion_context = self._build_emotion_context(detected_emotion)
        
        # Build language instruction based on frontend-provided language code
        language_map = {
            'es': 'ESPAÑOL',
            'en': 'English',
            'pt': 'Português',
            'fr': 'Français'
        }
        target_language = language_map.get(language, 'ESPAÑOL')
        
        language_instruction = f"IMPORTANTE: Responde en {target_language}. Todo el contenido debe estar en {target_language.lower()}."
        
        # Build age-appropriate instruction
        age_instruction = self._get_age_appropriate_instruction(age)
        
        # Create comprehensive prompt
        system_prompt = f"""You are an expert Content Adapter Agent for adaptive learning.

{language_instruction}

STUDENT PROFILE:
- Alias: {user_alias}
- Age: {age} years old
{age_instruction}

TASK: Generate educational content chunks about the topic provided by the user.

STYLE: {learning_style}
{style_instructions}

EMOTION CONTEXT: {emotion_context}

OUTPUT FORMAT (STRICT JSON ARRAY):
Return ONLY a JSON array of content chunks. Each chunk must be:
- text chunk: {{"type": "text", "content": "Educational explanation (max 40 words)"}}
- image_prompt chunk: {{"type": "image_prompt", "content": "Detailed visual description for image generation"}}

Example:
[
    {{"type": "text", "content": "Introduction to the concept..."}},
    {{"type": "text", "content": "Key points explained..."}},
    {{"type": "image_prompt", "content": "A detailed diagram showing..."}}
]

RULES:
- Keep text chunks SHORT and conversational (max 40 words)
- For "Mixto" style: Follow pattern of 2 text chunks, then 1 image_prompt
- For "Visual" style: Include image_prompts frequently (after every 1-2 text chunks)
- For "Lectura" style: Mostly text, minimal images
- NO markdown formatting, NO code blocks
- Return ONLY the JSON array
- LANGUAGE: {language_instruction}
"""
        
        user_prompt = f"Generate educational content about: {user_input}"

        try:
            # REAL CALL TO GEMINI PRO
            response = self._generate_content(
                contents=[system_prompt, user_prompt],
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    temperature=0.7
                )
            )
            
            # Validate response
            if not response or not response.text:
                logger.error("❌ [ContentAdapter] Empty response from Gemini API")
                return [{
                    "type": "text",
                    "content": f"Lo siento, hubo un problema generando el contenido. Por favor intenta de nuevo."
                }]
            
            # Parse response
            raw_text = response.text.strip()
            
            # Clean markdown if present
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text.replace("```", "").strip()
            
            content_chunks = json.loads(raw_text)
            
            logger.info(f"✅ [ContentAdapter] Generated {len(content_chunks)} chunks from Gemini")
            
            # POST-PROCESS: Add image URLs to image_prompt chunks
            processed_chunks = self._add_image_urls(content_chunks)
            
            # Log image URLs for debugging
            image_count = sum(1 for c in processed_chunks if c.get('type') == 'image_prompt')
            logger.info(f"📸 [ContentAdapter] Added URLs to {image_count} image chunks")
            
            # Log first image for verification
            first_image = next((c for c in processed_chunks if c.get('type') == 'image_prompt'), None)
            if first_image:
                logger.info(f"🖼️  [ContentAdapter] First image URL: {first_image.get('image_url', 'MISSING')}")
            
            return processed_chunks
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ [ContentAdapter] JSON parsing error: {e}")
            logger.error(f"Raw response: {raw_text[:200]}")
            
            # Fallback: return simple text chunk
            return [{
                "type": "text",
                "content": f"Contenido sobre {user_input} (error en generación JSON)"
            }]
            
        except Exception as e:
            logger.error(f"❌ [ContentAdapter] Error calling Gemini: {e}", exc_info=True)
            
            # Fallback
            return [{
                "type": "text",
                "content": f"Error generando contenido sobre {user_input}: {str(e)}"
            }]
    
    def _get_style_instructions(self, style: str) -> str:
        """Return style-specific generation instructions"""
        instructions = {
            "Mixto": "MANDATORY: Follow strict pattern of 2 text chunks, then 1 image_prompt. Repeat.",
            "Visual": "Include image_prompts frequently (after every 1-2 text chunks). Emphasize visual descriptions.",
            "Lectura": "Focus on detailed text explanations. Include images only when absolutely necessary (1 per 4-5 text chunks).",
            "Auditivo": "Use descriptive, narrative language. Include conversational tone. Minimal images."
        }
        return instructions.get(style, instructions["Mixto"])
    
    def _build_emotion_context(self, emotion_data: dict) -> str:
        """Build context string for emotion-based adaptation"""
        emotion = emotion_data.get('emotion', 'neutral')
        
        adaptations = {
            'confused': 'User is CONFUSED. Simplify language, add visual aids, break down concepts into smaller parts.',
            'bored': 'User is BORED. Make content more engaging, add interesting facts, use analogies and real-world examples.',
            'frustrated': 'User is FRUSTRATED. Be encouraging, slow down pace, provide reassurance and positive reinforcement.',
            'engaged': 'User is ENGAGED. Maintain current level, add depth, challenge with interesting details.',
            'neutral': 'User is NEUTRAL. Maintain balanced pace and moderate complexity.'
        }
        
        return adaptations.get(emotion, adaptations['neutral'])
    
    def _get_age_appropriate_instruction(self, age: int) -> str:
        """Build age-appropriate content guidance"""
        if age < 12:
            return "- Use simple vocabulary and short sentences\n- Include playful examples and analogies\n- Avoid complex terminology"
        elif age < 16:
            return "- Use clear language appropriate for teenagers\n- Connect concepts to relatable real-world situations\n- Balance simplicity with intellectual challenge"
        elif age < 25:
            return "- Use standard academic language\n- Include practical applications and critical thinking\n- Encourage deeper analysis"
        else:
            return "- Use professional and sophisticated language\n- Include advanced concepts and nuanced perspectives\n- Assume strong foundational knowledge"
    
    def _add_image_urls(self, chunks: list) -> list:
        """Add image_url and alt_text to all image_prompt chunks"""
        processed = []
        image_index = 0
        
        for chunk in chunks:
            if chunk.get('type') == 'image_prompt':
                # Generate image URL from prompt
                prompt = chunk.get('content', '')
                if not prompt:
                    logger.warning("⚠️  [ContentAdapter] image_prompt chunk has no content")
                    continue
                
                image_url = self._generate_image_url(prompt, image_index)
                image_index += 1
                
                logger.debug(f"🔗 [ContentAdapter] Generated URL for image {image_index}: {image_url}")
                
                processed.append({
                    "type": "image_prompt",
                    "content": prompt,
                    "image_url": image_url,
                    "alt_text": prompt[:100]
                })
            else:
                processed.append(chunk)
        
        return processed
