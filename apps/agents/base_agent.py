"""
Base Agent class for KAIROS multi-agent system.
All specialized agents inherit from this class.
"""
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))


class BaseAgent(ABC):
    """
    Abstract base class for all KAIROS agents.
    Provides common functionality for Gemini API interaction.
    """
    
    def __init__(self, model_name: str):
        """
        Initialize agent with specified Gemini model.
        
        Args:
            model_name: Name of Gemini model (e.g., 'gemini-3.0-pro', 'gemini-3.0-flash')
        """
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return result.
        Must be implemented by all child agents.
        
        Args:
            input_data: Input data specific to the agent
            
        Returns:
            Dict containing agent's output
        """
        pass
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """
        Generate content using Gemini model.
        
        Args:
            prompt: Text prompt for generation
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
        try:
            config = {**self.generation_config, **kwargs}
            response = await self.model.generate_content_async(
                prompt,
                generation_config=config
            )
            return response.text
        except Exception as e:
            print(f"Error generating content: {e}")
            return ""
    
    async def generate_content_with_image(self, prompt: str, image_data: bytes, **kwargs) -> str:
        """
        Generate content using both text and image input.
        
        Args:
            prompt: Text prompt
            image_data: Image bytes
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
        try:
            config = {**self.generation_config, **kwargs}
            response = await self.model.generate_content_async(
                [prompt, {"mime_type": "image/jpeg", "data": image_data}],
                generation_config=config
            )
            return response.text
        except Exception as e:
            print(f"Error generating content with image: {e}")
            return ""
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model."""
        return {
            "model_name": self.model_name,
            "agent_type": self.__class__.__name__
        }
