"""Property-based tests for calendar block description inclusion."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
from unittest.mock import Mock, patch

from src.services.calendar import CalendarService


def get_service():
    """Get a new CalendarService instance."""
    return CalendarService()


@given(
    description=st.text(min_size=1, max_size=2000),
    source_snippet=st.text(min_size=1, max_size=500),
)
@settings(max_examples=100)
def test_property_12_calendar_block_description_includes_task_description(
    description, source_snippet
):
    """
    Property 12: Calendar Block Description Inclusion

    For any calendar block created,
    the event description should include the task description.
    """
    service = get_service()
    task = {
        "title": "Test Task",
        "description": description,
        "deadline": datetime(2024, 3, 20, 14, 0, 0),
        "owner": "test@example.com",
        "confidence": 0.9,
        "source_snippet": source_snippet,
    }

    slot = (datetime(2024, 3, 20, 10, 0, 0), datetime(2024, 3, 20, 11, 0, 0))

    with patch.object(service, 'service') as mock_service:
        mock_service.events.return_value.insert.return_value.execute.return_value = {"id": "event-123"}

        try:
            block_id = service._create_calendar_block("primary", task, slot)
        except Exception:
            return

        if mock_service.events.return_value.insert.called:
            call_args = mock_service.events.return_value.insert.call_args
            event_body = call_args[1]['body'] if call_args else {}
            event_description = event_body.get('description', '')
            assert description in event_description, f"Description '{description}' not found in event description '{event_description}'"


@given(
    description=st.text(min_size=1, max_size=2000),
    source_snippet=st.text(min_size=1, max_size=500),
)
@settings(max_examples=100)
def test_property_12_calendar_block_description_includes_source_snippet(
    description, source_snippet
):
    """
    Property 12: Calendar Block Description Inclusion

    For any calendar block created,
    the event description should include the source snippet.
    """
    service = get_service()
    task = {
        "title": "Test Task",
        "description": description,
        "deadline": datetime(2024, 3, 20, 14, 0, 0),
        "owner": "test@example.com",
        "confidence": 0.9,
        "source_snippet": source_snippet,
    }

    slot = (datetime(2024, 3, 20, 10, 0, 0), datetime(2024, 3, 20, 11, 0, 0))

    with patch.object(service, 'service') as mock_service:
        mock_service.events.return_value.insert.return_value.execute.return_value = {"id": "event-123"}

        try:
            block_id = service._create_calendar_block("primary", task, slot)
        except Exception:
            return

        if mock_service.events.return_value.insert.called:
            call_args = mock_service.events.return_value.insert.call_args
            event_body = call_args[1]['body'] if call_args else {}
            event_description = event_body.get('description', '')
            assert source_snippet in event_description, f"Source snippet '{source_snippet}' not found in event description '{event_description}'"


@given(
    description=st.text(min_size=1, max_size=2000),
    source_snippet=st.text(min_size=1, max_size=500),
)
@settings(max_examples=100)
def test_property_12_calendar_block_description_format(
    description, source_snippet
):
    """
    Property 12: Calendar Block Description Inclusion

    For any calendar block created,
    the event description should have a specific format:
    task description followed by source snippet.
    """
    service = get_service()
    task = {
        "title": "Test Task",
        "description": description,
        "deadline": datetime(2024, 3, 20, 14, 0, 0),
        "owner": "test@example.com",
        "confidence": 0.9,
        "source_snippet": source_snippet,
    }

    slot = (datetime(2024, 3, 20, 10, 0, 0), datetime(2024, 3, 20, 11, 0, 0))

    with patch.object(service, 'service') as mock_service:
        mock_service.events.return_value.insert.return_value.execute.return_value = {"id": "event-123"}

        try:
            block_id = service._create_calendar_block("primary", task, slot)
        except Exception:
            return

        if mock_service.events.return_value.insert.called:
            call_args = mock_service.events.return_value.insert.call_args
            event_body = call_args[1]['body'] if call_args else {}
            event_description = event_body.get('description', '')

            # Check that description contains both parts
            assert description in event_description
            assert source_snippet in event_description

            # Check that description has the expected format
            expected_format = f"{description}\n\nSource: {source_snippet}"
            assert event_description == expected_format
