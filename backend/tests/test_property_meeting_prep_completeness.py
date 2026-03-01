"""
Property-based tests for meeting prep document completeness.

Feature: ai-execution-agent, Property 14: Meeting Prep Document Completeness
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hypothesis import given, strategies as st, settings
from datetime import datetime
from unittest.mock import Mock
import json

from backend.src.services.meeting_prep import MeetingPrepService
from backend.models.models import EmailContentModel, MeetingPrepDocument


@st.composite
def meeting_task(draw):
    """Generate a meeting task."""
    return {
        "title": draw(st.text(min_size=5, max_size=100)),
        "description": draw(st.text(min_size=10, max_size=200)),
        "deadline": datetime(2024, 3, 20, 14, 0, 0),
        "owner": draw(st.emails()),
        "confidence": draw(st.floats(min_value=0.0, max_value=1.0)),
        "source_snippet": draw(st.text(min_size=10, max_size=100))
    }


@st.composite
def email_content(draw):
    """Generate email content."""
    return EmailContentModel(
        subject=draw(st.text(min_size=5, max_size=100)),
        body=draw(st.text(min_size=20, max_size=500)),
        sender=draw(st.emails()),
        timestamp=draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2025, 12, 31))).isoformat() + 'Z'
    )


@st.composite
def complete_prep_document_json(draw):
    """Generate a complete prep document JSON response."""
    return {
        "context_summary": draw(st.text(min_size=20, max_size=200)),
        "talking_points": draw(st.lists(st.text(min_size=5, max_size=50), min_size=3, max_size=5)),
        "questions": draw(st.lists(st.text(min_size=10, max_size=100), min_size=3, max_size=5)),
        "risks": draw(st.lists(st.text(min_size=10, max_size=100), min_size=2, max_size=3))
    }


class TestPropertyMeetingPrepCompleteness:
    """Property-based tests for meeting prep document completeness."""

    @given(meeting_task(), email_content(), complete_prep_document_json())
    @settings(max_examples=100)
    def test_prep_document_completeness(self, task, email, prep_json):
        """
        Property 14: Meeting Prep Document Completeness
        
        For any generated meeting prep document, it should contain all required sections:
        context_summary, talking_points, questions, and risks, with each section being non-empty.
        
        Validates: Requirements 6.3, 6.4, 6.5, 6.6
        """
        # Feature: ai-execution-agent, Property 14: Meeting Prep Document Completeness
        
        # Mock LLM client to return the generated prep document
        mock_llm = Mock()
        mock_llm.complete.return_value = json.dumps(prep_json)
        
        service = MeetingPrepService(llm_client=mock_llm)
        
        # Generate prep document
        result = service._generate_prep_document(task, email)
        
        # Verify result is a MeetingPrepDocument
        assert isinstance(result, MeetingPrepDocument), (
            "Result should be a MeetingPrepDocument instance"
        )
        
        # Verify all required sections are present and non-empty
        assert result.context_summary, (
            "context_summary should be non-empty"
        )
        assert isinstance(result.context_summary, str), (
            "context_summary should be a string"
        )
        
        assert result.talking_points, (
            "talking_points should be non-empty"
        )
        assert isinstance(result.talking_points, list), (
            "talking_points should be a list"
        )
        assert len(result.talking_points) > 0, (
            "talking_points should contain at least one item"
        )
        
        assert result.questions, (
            "questions should be non-empty"
        )
        assert isinstance(result.questions, list), (
            "questions should be a list"
        )
        assert len(result.questions) > 0, (
            "questions should contain at least one item"
        )
        
        assert result.risks, (
            "risks should be non-empty"
        )
        assert isinstance(result.risks, list), (
            "risks should be a list"
        )
        assert len(result.risks) > 0, (
            "risks should contain at least one item"
        )
        
        # Verify meeting metadata is preserved
        assert result.meeting_title == task['title'], (
            "meeting_title should match task title"
        )
        assert result.meeting_time == task['deadline'], (
            "meeting_time should match task deadline"
        )

    @given(meeting_task(), email_content(), complete_prep_document_json())
    @settings(max_examples=100)
    def test_prep_document_all_sections_have_content(self, task, email, prep_json):
        """
        Property 14: Meeting Prep Document Completeness (content verification)
        
        For any generated meeting prep document, each section should have actual content
        (not just empty strings or empty lists).
        
        Validates: Requirements 6.3, 6.4, 6.5, 6.6
        """
        # Feature: ai-execution-agent, Property 14: Meeting Prep Document Completeness
        
        # Mock LLM client to return the generated prep document
        mock_llm = Mock()
        mock_llm.complete.return_value = json.dumps(prep_json)
        
        service = MeetingPrepService(llm_client=mock_llm)
        
        # Generate prep document
        result = service._generate_prep_document(task, email)
        
        # Verify context_summary has content
        assert len(result.context_summary.strip()) > 0, (
            "context_summary should have actual content, not just whitespace"
        )
        
        # Verify talking_points all have content
        for i, point in enumerate(result.talking_points):
            assert isinstance(point, str), (
                f"talking_points[{i}] should be a string"
            )
            assert len(point.strip()) > 0, (
                f"talking_points[{i}] should have actual content"
            )
        
        # Verify questions all have content
        for i, question in enumerate(result.questions):
            assert isinstance(question, str), (
                f"questions[{i}] should be a string"
            )
            assert len(question.strip()) > 0, (
                f"questions[{i}] should have actual content"
            )
        
        # Verify risks all have content
        for i, risk in enumerate(result.risks):
            assert isinstance(risk, str), (
                f"risks[{i}] should be a string"
            )
            assert len(risk.strip()) > 0, (
                f"risks[{i}] should have actual content"
            )
