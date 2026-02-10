from google import genai
from google.genai import types
import os
from abc import ABC, abstractmethod
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class KairosAgent(ABC):
    """
    Base class for all KAIROS agents.
    Provides shared utilities and configurable model selection.
    Models are now configurable via .env (GEMINI_FLASH_MODEL and GEMINI_PRO_MODEL)
    """

    def __init__(self):
        # Allowed models - Loaded from .env
        # Flash model (fast, cheaper, for camera/emotion)
        self.MODEL_FLASH = getattr(settings, 'GEMINI_FLASH_MODEL', 'gemini-3-flash-preview')
        # Pro model (powerful, for reasoning/content)
        self.MODEL_PRO = getattr(settings, 'GEMINI_PRO_MODEL', 'gemini-3-pro-preview')

        self.api_key = getattr(settings, "GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in settings or environment variables.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = self.get_model_name()
        self.validate_model_name()
        
        # Log agent initialization
        agent_name = self.__class__.__name__
        logger.info(f"[{agent_name}] Initialized with model: {self.model_name}")

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Must return one of the allowed model constants (MODEL_FLASH or MODEL_PRO).
        """
        pass

    def validate_model_name(self):
        """Ensures the agent uses a valid Gemini model."""
        allowed_models = [
            # Strictly Gemini 3 for this implementation
            'gemini-3-pro-preview',
            'gemini-3-flash-preview',
            'gemini-3.0-pro',
            'gemini-3.0-flash'
        ]
        
        # Check if model name contains any of the allowed patterns
        is_valid = any(allowed in self.model_name for allowed in allowed_models)
        
        if not is_valid:
            logger.warning(f"Model '{self.model_name}' not in standard whitelist. Proceeding in Experimental Mode.")

    def _generate_content(self, contents, config: types.GenerateContentConfig = None) -> types.GenerateContentResponse:
        """
        Helper to generate content using google-genai SDK.
        Includes permissive safety settings for Educational Content.
        """
        try:
            if config is None:
                config = types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95,
                    max_output_tokens=2048,
                    # 👇 CONFIGURACIÓN DE SEGURIDAD MODIFICADA PARA EDUCACIÓN SEXUAL 👇
                    safety_settings=[
                        types.SafetySetting(
                            category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
                            # 'BLOCK_NONE' permite contenido educativo/biológico sobre sexo.
                            # 'BLOCK_ONLY_HIGH' a veces sigue censurando.
                            threshold='BLOCK_NONE' 
                        ),
                        types.SafetySetting(
                            category='HARM_CATEGORY_HARASSMENT',
                            threshold='BLOCK_ONLY_HIGH'
                        ),
                        types.SafetySetting(
                            category='HARM_CATEGORY_HATE_SPEECH',
                            threshold='BLOCK_ONLY_HIGH'
                        ),
                        types.SafetySetting(
                            category='HARM_CATEGORY_DANGEROUS_CONTENT',
                            threshold='BLOCK_ONLY_HIGH'
                        )
                    ]
                )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            
            # Check if response was blocked by safety filters
            if response and not response.text:
                logger.warning(f"⚠️ [{self.__class__.__name__}] Response has no text (possibly blocked by safety filters)")
                if hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate, 'finish_reason'):
                            logger.warning(f"   Finish reason: {candidate.finish_reason}")
                        if hasattr(candidate, 'safety_ratings'):
                            logger.warning(f"   Safety ratings: {candidate.safety_ratings}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ [{self.__class__.__name__}] Gemini API error: {e}", exc_info=True)
            raise

    @abstractmethod
    async def process(self, input_data: dict) -> dict | list:
        """
        Main processing method for the agent.
        """
        agent_name = self.__class__.__name__
        logger.info(f"🔄 [{agent_name}] Processing started")
        pass