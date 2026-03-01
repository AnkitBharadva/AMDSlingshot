"""LLM client abstraction for OpenAI and Gemini integration.

This module provides a unified interface for interacting with different LLM providers
(OpenAI, Google Gemini). It defines an abstract base class and concrete implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional
import os


class LLMClient(ABC):
    """
    Abstract base class for LLM clients.
    
    Provides a unified interface for different LLM providers.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the LLM client.
        
        Args:
            api_key: API key for the LLM provider. If not provided, 
                     will attempt to read from environment variable.
            model: Model name to use. If not provided, will use default.
        """
        self.api_key = api_key or self._get_api_key_from_env()
        self.model = model or self._get_default_model()
    
    @abstractmethod
    def _get_api_key_from_env(self) -> str:
        """Get API key from environment variable."""
        pass
    
    @abstractmethod
    def _get_default_model(self) -> str:
        """Get default model name."""
        pass
    
    @abstractmethod
    def complete(self, prompt: str) -> str:
        """
        Send a prompt to the LLM and get a completion.
        
        Args:
            prompt: The prompt to send to the LLM.
            
        Returns:
            The LLM's completion as a string.
        """
        pass
    
    def get_model_name(self) -> str:
        """Get the current model name."""
        return self.model


class OpenAIClient(LLMClient):
    """
    OpenAI LLM client implementation.
    
    Uses the OpenAI API for task extraction and document generation.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key. If not provided, reads from OPENAI_API_KEY env var.
            model: Model name (e.g., 'gpt-4', 'gpt-3.5-turbo'). Defaults to 'gpt-4'.
        """
        super().__init__(api_key, model)
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
    
    def _get_api_key_from_env(self) -> str:
        """Get OpenAI API key from environment."""
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Please set it to use OpenAI LLM client."
            )
        return api_key
    
    def _get_default_model(self) -> str:
        """Get default OpenAI model from environment or use gpt-3.5-turbo."""
        return os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    def complete(self, prompt: str) -> str:
        """
        Send a prompt to OpenAI's API and get a completion.
        
        Args:
            prompt: The prompt to send to the LLM.
            
        Returns:
            The LLM's completion as a string.
            
        Raises:
            RuntimeError: If the API call fails.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that returns structured data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")


class GeminiClient(LLMClient):
    """
    Google Gemini LLM client implementation.
    
    Uses the Google Gemini API for task extraction and document generation.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the Gemini client.
        
        Args:
            api_key: Gemini API key. If not provided, reads from GEMINI_API_KEY env var.
            model: Model name (e.g., 'gemini-pro', 'gemini-1.5-pro'). Defaults to 'gemini-pro'.
        """
        super().__init__(api_key, model)
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self._model_instance = genai.GenerativeModel(self.model)
    
    def _get_api_key_from_env(self) -> str:
        """Get Gemini API key from environment."""
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable not set. "
                "Please set it to use Gemini LLM client."
            )
        return api_key
    
    def _get_default_model(self) -> str:
        """Get default Gemini model from environment or use gemini-1.5-flash."""
        return os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')
    
    def complete(self, prompt: str) -> str:
        """
        Send a prompt to Gemini API and get a completion.
        
        Args:
            prompt: The prompt to send to the LLM.
            
        Returns:
            The LLM's completion as a string.
            
        Raises:
            RuntimeError: If the API call fails.
        """
        try:
            response = self._model_instance.generate_content(prompt)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")
