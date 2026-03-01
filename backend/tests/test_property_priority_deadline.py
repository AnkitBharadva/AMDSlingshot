"""Property-based tests for deadline-based priority assignment."""

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
    hours_until_deadline=st.floats(min_value=0, max_value=23.9),
    has_urgent_keyword=st.booleans(),
)
@settings(max_examples=100)
def test_property_5_high_priority_when_deadline_less_than_24_hours(
    hours_until_deadline, has_urgent_keyword
):
    """
    Property 5: Deadline-Based Priority Assignment

    For any task with deadline less than 24 hours away,
    the priority should be "high".
    """
    service = get_service()
    task = {
        "title": "Test Task" + (" URGENT" if has_urgent_keyword else ""),
        "description": "Test Description",
        "deadline": datetime.now() + timedelta(hours=hours_until_deadline),
        "owner": "test@example.com",
        "confidence": 0.9,
        "source_snippet": "Test",
    }

    current_time = datetime.now()
    result = service._assign_priority(task, current_time)

    assert result["priority"] == "high", f"Expected high priority for deadline < 24h, got {result['priority']}"


@given(
    hours_until_deadline=st.floats(min_value=24.1, max_value=168),  # > 24h to 7 days
    has_urgent_keyword=st.booleans(),
)
@settings(max_examples=100)
def test_property_5_medium_priority_when_deadline_24_hours_or_more(
    hours_until_deadline, has_urgent_keyword
):
    """
    Property 5: Deadline-Based Priority Assignment

    For any task with deadline 24 hours or more away,
    the priority should be "medium" (unless urgent keyword present).
    """
    service = get_service()
    task = {
        "title": "Test Task" + (" URGENT" if has_urgent_keyword else ""),
        "description": "Test Description",
        "deadline": datetime.now() + timedelta(hours=hours_until_deadline),
        "owner": "test@example.com",
        "confidence": 0.9,
        "source_snippet": "Test",
    }

    current_time = datetime.now()
    result = service._assign_priority(task, current_time)

    if has_urgent_keyword:
        assert result["priority"] == "high"
    else:
        assert result["priority"] == "medium"


@given(
    hours_until_deadline=st.floats(min_value=0, max_value=23.9),
    has_urgent_keyword=st.just(True),
)
@settings(max_examples=100)
def test_property_5_urgent_keyword_overrides_deadline(
    hours_until_deadline, has_urgent_keyword
):
    """
    Property 5: Deadline-Based Priority Assignment

    For any task with urgent keyword, priority should be "high"
    regardless of deadline.
    """
    service = get_service()
    task = {
        "title": "URGENT: Test Task",
        "description": "URGENT: Test Description",
        "deadline": datetime.now() + timedelta(hours=hours_until_deadline),
        "owner": "test@example.com",
        "confidence": 0.9,
        "source_snippet": "URGENT: Test",
    }

    current_time = datetime.now()
    result = service._assign_priority(task, current_time)

    assert result["priority"] == "high"
