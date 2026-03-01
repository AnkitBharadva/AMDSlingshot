"""Tests for meeting prep service."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from datetime import datetime
from unittest.mock import Mock

from backend.models.models import EmailContentModel, MeetingPrepDocument
from backend.src.services.meeting_prep import MeetingPrepService


class TestMeetingPrepService:
    """Tests for MeetingPrepService."""

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client."""
        mock = Mock()
        return mock

    @pytest.fixture
    def service(self, mock_llm_client):
        """Meeting prep service with mock client."""
        return MeetingPrepService(llm_client=mock_llm_client)

    def test_is_meeting_with_keywords(self, service):
        """Test meeting detection with keywords."""
        task = {
            "title": "Project Meeting",
            "description": "Discuss project timeline",
        }

        result = service._is_meeting(task)

        assert result is True

    def test_is_meeting_without_keywords(self, service):
        """Test non-meeting detection."""
        task = {
            "title": "Fix Bug",
            "description": "Fix production bug",
        }

        result = service._is_meeting(task)

        assert result is False

    def test_detect_and_generate_prep_meeting(self, service, mock_llm_client):
        """Test prep document generation for meeting."""
        mock_llm_client.complete.return_value = """{
            "context_summary": "Meeting to discuss project timeline.",
            "talking_points": ["Timeline", "Milestones", "Resources"],
            "questions": ["What is the deadline?", "What resources are needed?"],
            "risks": ["Timeline slippage", "Resource constraints"]
        }"""

        task = {
            "title": "Project Meeting",
            "description": "Discuss project timeline",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": "john@example.com",
            "confidence": 0.9,
            "source_snippet": "Let's schedule a meeting.",
        }

        email_content = EmailContentModel(
            subject="Meeting Request",
            body="Can we schedule a meeting?",
            sender="john@example.com",
            timestamp="2024-03-15T10:00:00Z",
        )

        result = service.detect_and_generate_prep(task, email_content)

        assert isinstance(result, MeetingPrepDocument)
        assert result.meeting_title == "Project Meeting"

    def test_detect_and_generate_prep_not_meeting(self, service, mock_llm_client):
        """Test no prep document for non-meeting task."""
        task = {
            "title": "Fix Bug",
            "description": "Fix production bug",
        }

        email_content = EmailContentModel(
            subject="Bug Report",
            body="Please fix this bug",
            sender="john@example.com",
            timestamp="2024-03-15T10:00:00Z",
        )

        result = service.detect_and_generate_prep(task, email_content)

        assert result is None

    def test_build_prep_prompt(self, service):
        """Test prep prompt building."""
        task = {
            "title": "Project Meeting",
            "description": "Discuss project timeline",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
        }

        email_content = EmailContentModel(
            subject="Meeting Request",
            body="Can we schedule a meeting?",
            sender="john@example.com",
            timestamp="2024-03-15T10:00:00Z",
        )

        prompt = service._build_prep_prompt(task, email_content)

        assert "Project Meeting" in prompt
        assert "Discuss project timeline" in prompt
        assert "Meeting Request" in prompt

    def test_parse_prep_response(self, service):
        """Test prep response parsing."""
        response = """{
            "context_summary": "Meeting to discuss project timeline.",
            "talking_points": ["Timeline", "Milestones"],
            "questions": ["What is the deadline?"],
            "risks": ["Timeline slippage"]
        }"""

        task = {
            "title": "Project Meeting",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
        }

        result = service._parse_prep_response(response, task)

        assert isinstance(result, MeetingPrepDocument)
        assert result.context_summary == "Meeting to discuss project timeline."
        assert len(result.talking_points) == 2

    def test_is_meeting_with_various_keywords(self, service):
        """Test meeting detection with various meeting keywords."""
        keywords = ["meeting", "call", "discussion", "sync", "standup", 
                   "review", "demo", "presentation", "interview"]
        
        for keyword in keywords:
            task = {
                "title": f"Project {keyword}",
                "description": "Discuss project details",
            }
            result = service._is_meeting(task)
            assert result is True, f"Task with keyword '{keyword}' should be detected as meeting"
            
            # Test with keyword in description
            task = {
                "title": "Project Task",
                "description": f"We need to have a {keyword} about this",
            }
            result = service._is_meeting(task)
            assert result is True, f"Task with keyword '{keyword}' in description should be detected as meeting"

    def test_is_meeting_case_insensitive(self, service):
        """Test meeting detection is case-insensitive."""
        task = {
            "title": "PROJECT MEETING",
            "description": "DISCUSS PROJECT TIMELINE",
        }
        result = service._is_meeting(task)
        assert result is True

        task = {
            "title": "project meeting",
            "description": "discuss project timeline",
        }
        result = service._is_meeting(task)
        assert result is True

    def test_llm_integration_with_mocked_response(self, service, mock_llm_client):
        """Test LLM integration with mocked responses."""
        # Test with valid JSON response
        mock_llm_client.complete.return_value = """{
            "context_summary": "Test summary",
            "talking_points": ["Point 1", "Point 2", "Point 3"],
            "questions": ["Question 1", "Question 2", "Question 3"],
            "risks": ["Risk 1", "Risk 2"]
        }"""

        task = {
            "title": "Team Sync",
            "description": "Weekly team sync",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": "john@example.com",
            "confidence": 0.9,
            "source_snippet": "Weekly sync meeting",
        }

        email_content = EmailContentModel(
            subject="Weekly Sync",
            body="Let's have our weekly sync",
            sender="john@example.com",
            timestamp="2024-03-15T10:00:00Z",
        )

        result = service.detect_and_generate_prep(task, email_content)

        # Verify LLM was called
        assert mock_llm_client.complete.called
        
        # Verify result structure
        assert isinstance(result, MeetingPrepDocument)
        assert result.context_summary == "Test summary"
        assert len(result.talking_points) == 3
        assert len(result.questions) == 3
        assert len(result.risks) == 2

    def test_parse_prep_response_with_json_in_text(self, service):
        """Test parsing JSON response embedded in text."""
        response = """Here is the meeting prep document:
        {
            "context_summary": "Meeting about project status.",
            "talking_points": ["Status update", "Next steps"],
            "questions": ["What are the blockers?"],
            "risks": ["Delayed timeline"]
        }
        That's all!"""

        task = {
            "title": "Status Meeting",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
        }

        result = service._parse_prep_response(response, task)

        assert isinstance(result, MeetingPrepDocument)
        assert result.context_summary == "Meeting about project status."
        assert len(result.talking_points) == 2
