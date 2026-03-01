"""Property-based tests for keyword-based priority elevation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta

from src.services.post_processing import PostProcessingService


def get_service():
    """Get a new PostProcessingService instance."""
    return PostProcessingService()


@given(
    keyword=st.sampled_from(["urgent", "asap", "immediately", "critical", "emergency"]),
    hours_until_deadline=st.floats(min_value=24.1, max_value=168),
)
@settings(max_examples=100)
def test_property_6_urgent_keywords_elevate_priority(
    keyword, hours_until_deadline
):
    """
    Property 6: Keyword-Based Priority Elevation

    For any task containing urgent keywords in title or description,
    the priority should be elevated to "high".
    """
    service = get_service()
    task = {
        "title": f"{keyword.upper()}: Test Task",
        "description": f"Test Description with {keyword}",
        "deadline": datetime.now() + timedelta(hours=hours_until_deadline),
        "owner": "test@example.com",
        "confidence": 0.9,
        "source_snippet": f"Test with {keyword}",
    }

    current_time = datetime.now()
    result = service._assign_priority(task, current_time)

    assert result["priority"] == "high", f"Keyword '{keyword}' should elevate priority to high"


@given(
    keyword=st.sampled_from(["urgent", "asap", "immediately", "critical", "emergency"]),
    hours_until_deadline=st.floats(min_value=24.1, max_value=168),
)
@settings(max_examples=100)
def test_property_6_urgent_keywords_in_description_elevate_priority(
    keyword, hours_until_deadline
):
    """
    Property 6: Keyword-Based Priority Elevation

    For any task with urgent keyword in description,
    the priority should be elevated to "high".
    """
    service = get_service()
    task = {
        "title": "Test Task",
        "description": f"Description with {keyword} requirement",
        "deadline": datetime.now() + timedelta(hours=hours_until_deadline),
        "owner": "test@example.com",
        "confidence": 0.9,
        "source_snippet": "Test",
    }

    current_time = datetime.now()
    result = service._assign_priority(task, current_time)

    assert result["priority"] == "high"


@given(
    keyword=st.sampled_from(["urgent", "asap", "immediately", "critical", "emergency"]),
    hours_until_deadline=st.floats(min_value=24.1, max_value=168),
)
@settings(max_examples=100)
def test_property_6_urgent_keywords_in_source_snippet_elevate_priority(
    keyword, hours_until_deadline
):
    """
    Property 6: Keyword-Based Priority Elevation

    For any task with urgent keyword in title or description,
    the priority should be elevated to "high".
    """
    service = get_service()
    task = {
        "title": f"Test Task with {keyword}",
        "description": f"Description with {keyword} note",
        "deadline": datetime.now() + timedelta(hours=hours_until_deadline),
        "owner": "test@example.com",
        "confidence": 0.9,
        "source_snippet": "Source text",
    }

    current_time = datetime.now()
    result = service._assign_priority(task, current_time)

    assert result["priority"] == "high"


@given(
    keyword=st.sampled_from(["urgent", "asap", "immediately", "critical", "emergency"]),
    hours_until_deadline=st.floats(min_value=24.1, max_value=168),
)
@settings(max_examples=100)
def test_property_6_case_insensitive_keyword_matching(
    keyword, hours_until_deadline
):
    """
    Property 6: Keyword-Based Priority Elevation

    For any task with urgent keyword in any case,
    the priority should be elevated to "high".
    """
    service = get_service()
    task = {
        "title": keyword.upper(),
        "description": keyword.capitalize(),
        "deadline": datetime.now() + timedelta(hours=hours_until_deadline),
        "owner": "test@example.com",
        "confidence": 0.9,
        "source_snippet": keyword.lower(),
    }

    current_time = datetime.now()
    result = service._assign_priority(task, current_time)

    assert result["priority"] == "high"
