"""Tests for task extraction service."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from datetime import datetime
from unittest.mock import Mock

from backend.models.models import EmailContentModel, ThreadMessageModel, ForwardedMessageModel
from backend.src.services.extraction import TaskExtractionService, ExtractionError


class TestTaskExtractionService:
    """Tests for TaskExtractionService."""

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client."""
        mock = Mock()
        return mock

    @pytest.fixture
    def extraction_service(self, mock_llm_client):
        """Task extraction service with mock client."""
        return TaskExtractionService(llm_client=mock_llm_client, max_retries=1)

    def test_extract_tasks_success(self, extraction_service, mock_llm_client):
        """Test successful task extraction."""
        # Mock LLM response
        mock_llm_client.complete.return_value = """[
            {
                "id": "task-001",
                "title": "Project Meeting",
                "description": "Discuss project timeline",
                "deadline": "2024-03-20T14:00:00Z",
                "owner": "john@example.com",
                "confidence": 0.9,
                "source_snippet": "Let's schedule a meeting."
            }
        ]"""

        email_content = EmailContentModel(
            subject="Test Subject",
            body="Test Body",
            sender="test@example.com",
            timestamp="2024-03-15T10:00:00Z",
        )

        tasks = extraction_service.extract_tasks(email_content)

        assert len(tasks) == 1
        assert tasks[0]["title"] == "Project Meeting"
        assert tasks[0]["confidence"] == 0.9

    def test_extract_tasks_with_retry(self, extraction_service, mock_llm_client):
        """Test task extraction with retry on JSON parse failure."""
        # First attempt returns invalid JSON, second attempt succeeds
        mock_llm_client.complete.side_effect = [
            "Invalid JSON response",
            """[
                {
                    "id": "task-001",
                    "title": "Project Meeting",
                    "description": "Discuss project timeline",
                    "deadline": "2024-03-20T14:00:00Z",
                    "owner": "john@example.com",
                    "confidence": 0.9,
                    "source_snippet": "Let's schedule a meeting."
                }
            ]""",
        ]

        email_content = EmailContentModel(
            subject="Test Subject",
            body="Test Body",
            sender="test@example.com",
            timestamp="2024-03-15T10:00:00Z",
        )

        tasks = extraction_service.extract_tasks(email_content)

        assert len(tasks) == 1
        assert tasks[0]["title"] == "Project Meeting"

    def test_extract_tasks_max_retries_exceeded(self, extraction_service, mock_llm_client):
        """Test task extraction fails after max retries."""
        # Always return invalid JSON
        mock_llm_client.complete.return_value = "Invalid JSON response"

        email_content = EmailContentModel(
            subject="Test Subject",
            body="Test Body",
            sender="test@example.com",
            timestamp="2024-03-15T10:00:00Z",
        )

        with pytest.raises(ExtractionError):
            extraction_service.extract_tasks(email_content)

    def test_extract_tasks_missing_required_field(self, extraction_service, mock_llm_client):
        """Test task extraction fails when required field is missing."""
        # LLM response missing required field
        mock_llm_client.complete.return_value = """[
            {
                "id": "task-001",
                "title": "Project Meeting",
                "description": "Discuss project timeline",
                "deadline": "2024-03-20T14:00:00Z",
                "owner": "john@example.com",
                "confidence": 0.9
                # Missing source_snippet
            }
        ]"""

        email_content = EmailContentModel(
            subject="Test Subject",
            body="Test Body",
            sender="test@example.com",
            timestamp="2024-03-15T10:00:00Z",
        )

        with pytest.raises(ExtractionError):
            extraction_service.extract_tasks(email_content)

    def test_extract_tasks_empty_response(self, extraction_service, mock_llm_client):
        """Test task extraction with empty response."""
        mock_llm_client.complete.return_value = "[]"

        email_content = EmailContentModel(
            subject="Test Subject",
            body="Test Body",
            sender="test@example.com",
            timestamp="2024-03-15T10:00:00Z",
        )

        tasks = extraction_service.extract_tasks(email_content)

        assert len(tasks) == 0

    def test_build_extraction_prompt_includes_thread_messages(self, extraction_service, mock_llm_client):
        """Test that extraction prompt includes thread messages."""
        email_content = EmailContentModel(
            subject="Test Subject",
            body="Test Body",
            sender="test@example.com",
            timestamp="2024-03-15T10:00:00Z",
            thread_messages=[
                ThreadMessageModel(
                    sender="sender@example.com",
                    timestamp="2024-03-15T09:00:00Z",
                    body="Thread message content"
                )
            ]
        )

        # Call the method to build prompt
        prompt = extraction_service._build_extraction_prompt(email_content)

        assert "Thread Messages:" in prompt
        assert "Thread message content" in prompt

    def test_build_extraction_prompt_includes_forwarded_messages(self, extraction_service, mock_llm_client):
        """Test that extraction prompt includes forwarded messages."""
        email_content = EmailContentModel(
            subject="Test Subject",
            body="Test Body",
            sender="test@example.com",
            timestamp="2024-03-15T10:00:00Z",
            forwarded_messages=[
                ForwardedMessageModel(
                    original_sender="original@example.com",
                    original_timestamp="2024-03-15T08:00:00Z",
                    body="Forwarded content"
                )
            ]
        )

        prompt = extraction_service._build_extraction_prompt(email_content)

        assert "Forwarded Messages:" in prompt
        assert "Forwarded content" in prompt

    def test_build_extraction_prompt_multilingual_support(self, extraction_service, mock_llm_client):
        """Test that extraction prompt includes multi-language support configuration."""
        email_content = EmailContentModel(
            subject="Reunión de Proyecto",
            body="Hola equipo, programemos una reunión para discutir el cronograma del proyecto.",
            sender="juan@example.com",
            timestamp="2024-03-15T10:00:00Z",
        )

        prompt = extraction_service._build_extraction_prompt(email_content)

        # Check that the prompt includes multi-language instructions
        assert "Preserve the original language" in prompt
        assert "any language" not in prompt.lower()  # Implementation uses "original language" phrasing

    def test_build_extraction_prompt_handles_non_english_email(self, extraction_service, mock_llm_client):
        """Test that extraction prompt correctly handles non-English email content."""
        email_content = EmailContentModel(
            subject="会议邀请",
            body="请安排一个会议讨论项目计划。",
            sender="li@example.com",
            timestamp="2024-03-15T10:00:00Z",
        )

        prompt = extraction_service._build_extraction_prompt(email_content)

        # Verify the non-English content is included in the prompt
        assert "会议邀请" in prompt
        assert "请安排一个会议讨论项目计划。" in prompt
