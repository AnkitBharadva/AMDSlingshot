"""Tests for LLM client abstraction."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestLLMClient:
    """Tests for LLM client base class and implementations."""

    def test_openai_client_initialization_with_api_key(self):
        """Test OpenAI client initialization with explicit API key."""
        from backend.src.services.llm_client import OpenAIClient
        
        with patch('openai.OpenAI') as mock_openai:
            client = OpenAIClient(api_key='test-key', model='gpt-3.5-turbo')
            assert client.api_key == 'test-key'
            assert client.model == 'gpt-3.5-turbo'
            mock_openai.assert_called_once_with(api_key='test-key')

    def test_openai_client_initialization_with_env_var(self):
        """Test OpenAI client initialization with environment variable."""
        from backend.src.services.llm_client import OpenAIClient
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'env-key'}):
            with patch('openai.OpenAI') as mock_openai:
                client = OpenAIClient(model='gpt-4')
                assert client.api_key == 'env-key'
                assert client.model == 'gpt-4'
                mock_openai.assert_called_once_with(api_key='env-key')

    def test_openai_client_initialization_missing_env_var(self):
        """Test OpenAI client raises error when env var is missing."""
        from backend.src.services.llm_client import OpenAIClient
        
        # Ensure env var is not set
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable not set"):
            OpenAIClient()

    def test_openai_client_default_model(self):
        """Test OpenAI client uses default model."""
        from backend.src.services.llm_client import OpenAIClient
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('openai.OpenAI'):
                client = OpenAIClient()
                assert client.model == 'gpt-4'

    def test_openai_client_complete_success(self):
        """Test OpenAI client successful completion."""
        from backend.src.services.llm_client import OpenAIClient
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test completion"))]
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('openai.OpenAI') as mock_openai_class:
                mock_client = Mock()
                mock_openai_class.return_value = mock_client
                mock_client.chat.completions.create.return_value = mock_response
                
                client = OpenAIClient()
                result = client.complete("Test prompt")
                
                assert result == "Test completion"
                mock_client.chat.completions.create.assert_called_once()

    def test_openai_client_complete_error(self):
        """Test OpenAI client handles API errors."""
        from backend.src.services.llm_client import OpenAIClient
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('openai.OpenAI') as mock_openai_class:
                mock_client = Mock()
                mock_openai_class.return_value = mock_client
                mock_client.chat.completions.create.side_effect = Exception("API Error")
                
                client = OpenAIClient()
                with pytest.raises(RuntimeError, match="OpenAI API error"):
                    client.complete("Test prompt")

    def test_gemini_client_initialization_with_api_key(self):
        """Test Gemini client initialization with explicit API key."""
        from backend.src.services.llm_client import GeminiClient
        
        with patch('google.generativeai.configure') as mock_configure:
            with patch('google.generativeai.GenerativeModel') as mock_model:
                client = GeminiClient(api_key='test-key', model='gemini-1.5-pro')
                assert client.api_key == 'test-key'
                assert client.model == 'gemini-1.5-pro'
                mock_configure.assert_called_once_with(api_key='test-key')
                mock_model.assert_called_once_with('gemini-1.5-pro')

    def test_gemini_client_initialization_with_env_var(self):
        """Test Gemini client initialization with environment variable."""
        from backend.src.services.llm_client import GeminiClient
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'env-key'}):
            with patch('google.generativeai.configure') as mock_configure:
                with patch('google.generativeai.GenerativeModel') as mock_model:
                    client = GeminiClient(model='gemini-pro')
                    assert client.api_key == 'env-key'
                    assert client.model == 'gemini-pro'
                    mock_configure.assert_called_once_with(api_key='env-key')

    def test_gemini_client_initialization_missing_env_var(self):
        """Test Gemini client raises error when env var is missing."""
        from backend.src.services.llm_client import GeminiClient
        
        # Ensure env var is not set
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        
        with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable not set"):
            GeminiClient()

    def test_gemini_client_default_model(self):
        """Test Gemini client uses default model."""
        from backend.src.services.llm_client import GeminiClient
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel'):
                    client = GeminiClient()
                    assert client.model == 'gemini-pro'

    def test_gemini_client_complete_success(self):
        """Test Gemini client successful completion."""
        from backend.src.services.llm_client import GeminiClient
        
        mock_response = Mock()
        mock_response.text = "Test completion"
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel') as mock_model_class:
                    mock_model = Mock()
                    mock_model_class.return_value = mock_model
                    mock_model.generate_content.return_value = mock_response
                    
                    client = GeminiClient()
                    result = client.complete("Test prompt")
                    
                    assert result == "Test completion"
                    mock_model.generate_content.assert_called_once_with("Test prompt")

    def test_gemini_client_complete_error(self):
        """Test Gemini client handles API errors."""
        from backend.src.services.llm_client import GeminiClient
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel') as mock_model_class:
                    mock_model = Mock()
                    mock_model_class.return_value = mock_model
                    mock_model.generate_content.side_effect = Exception("API Error")
                    
                    client = GeminiClient()
                    with pytest.raises(RuntimeError, match="Gemini API error"):
                        client.complete("Test prompt")

    def test_llm_client_get_model_name(self):
        """Test LLM client get_model_name method."""
        from backend.src.services.llm_client import OpenAIClient
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('openai.OpenAI'):
                client = OpenAIClient(model='custom-model')
                assert client.get_model_name() == 'custom-model'
