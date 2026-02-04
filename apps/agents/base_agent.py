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
    Enforces strict model selection (Gemini 3) and provides shared utilities.
    """

    # Allowed models
    MODEL_FLASH = "gemini-3-flash-preview"
    MODEL_PRO = "gemini-3-pro-preview"

    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in settings or environment variables.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = self.get_model_name()
        self.validate_model_name()
        
        # Log agent initialization
        agent_name = self.__class__.__name__
        logger.info(f"🤖 [{agent_name}] Initialized with model: {self.model_name}")
        # self.model is deprecated, use self.client in generation methods

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Must return one of the allowed model constants.
        """
        pass

    def validate_model_name(self):
        """Ensures the agent uses a strictly allowed Gemini 3 model."""
        if self.model_name not in [self.MODEL_FLASH, self.MODEL_PRO]:
            raise ValueError(
                f"Invalid model '{self.model_name}'. "
                f"Must be one of: {self.MODEL_FLASH}, {self.MODEL_PRO}"
            )

    async def _generate_content(self, info: dict) -> types.GenerateContentResponse:
        """
        Helper to generate content using the new SDK.
        Override/call this from process() methods.
        """
        # Note: The new SDK might specific async client or method.
        # Check docs or assume client.models.generate_content is sync, 
        # or client.aio.models.generate_content for async.
        # User prompt example used sync syntax: response = self.client.models.generate_content(...)
        # But we are in async methods.
        # Ideally we use client.aio for async.
        # Let's assume standard sync for now as per user snippet, 
        # but if this is an async method, we should likely wrap it or use the async client if available.
        # User snippet:
        # response = self.client.models.generate_content(
        #     model='gemini-3-pro-preview', 
        #     contents='Tu prompt aqui',
        #     config=types.GenerateContentConfig(...)
        # )
        
        # We'll use the sync call for now as requested, potentially blocking the loop, 
        # or relies on the user ensuring it's fast or wrapped. 
        # Ideally: response = await self.client.aio.models.generate_content(...) if exists.
        # Staying strict to user snippet first.
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Must return one of the allowed model constants.
        """
        pass

    def validate_model_name(self):
        """Ensures the agent uses a strictly allowed Gemini 3 model."""
        if self.model_name not in [self.MODEL_FLASH, self.MODEL_PRO]:
            raise ValueError(
                f"Invalid model '{self.model_name}'. "
                f"Must be one of: {self.MODEL_FLASH}, {self.MODEL_PRO}"
            )

    @abstractmethod
    async def process(self, input_data: dict) -> dict | list:
        """
        Main processing method for the agent.
        """
        agent_name = self.__class__.__name__
        logger.info(f"🔄 [{agent_name}] Processing started")
        pass
