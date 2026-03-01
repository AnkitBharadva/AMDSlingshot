"""Property-based tests for manual review no auto-schedule."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime

from src.services.orchestrator import AgentOrchestrator
from unittest.mock import Mock


def get_orchestrator():
    """Get a new AgentOrchestrator instance."""
    return AgentOrchestrator(
        extraction_service=Mock(),
        post_processing_service=Mock(),
        calendar_service=Mock(),
        meeting_prep_service=Mock(),
    )


@given(
    confidence=st.floats(min_value=0.0, max_value=0.69),
)
@settings(max_examples=100)
def test_property_16_manual_review_tasks_do_not_trigger_calendar(
    confidence
):
    """
    Property 16: Manual Review Tasks Not Auto-Scheduled

    For any task marked as manual_review,
    the calendar service should not be called to find slots.
    """
    orchestrator = get_orchestrator()
    mock_services = {
        'extraction': orchestrator.extraction,
        'post_processing': orchestrator.post_processing,
        'calendar': orchestrator.calendar,
        'meeting_prep': orchestrator.meeting_prep,
    }

    # Setup mocks
    mock_services['extraction'].extract_tasks.return_value = [
        {
            "id": "task-001",
            "title": "Test Task",
            "description": "Test Description",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": "test@example.com",
            "confidence": confidence,
            "priority": "medium",
            "state": "manual_review",
            "source_snippet": "Test",
        }
    ]

    mock_services['post_processing'].process_tasks.return_value = [
        {
            "id": "task-001",
            "title": "Test Task",
            "description": "Test Description",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": "test@example.com",
            "confidence": confidence,
            "priority": "medium",
            "state": "manual_review",
            "source_snippet": "Test",
        }
    ]

    mock_services['calendar'].find_slot_and_create_block.return_value = ("event-123", None)
    mock_services['meeting_prep'].detect_and_generate_prep.return_value = None

    from src.models.models import RunAgentRequestModel, EmailContentModel
    request = RunAgentRequestModel(
        email_content=EmailContentModel(
            subject="Test",
            body="Test",
            sender="test@example.com",
            timestamp="2024-03-15T10:00:00Z",
        ),
        user_timezone="America/New_York",
        calendar_id="primary",
    )

    response = orchestrator.run_agent(request)

    # Calendar should not be called for manual review tasks
    assert mock_services['calendar'].find_slot_and_create_block.call_count == 0


@given(
    confidence=st.floats(min_value=0.0, max_value=0.69),
)
@settings(max_examples=100)
def test_property_16_manual_review_tasks_do_not_create_calendar_blocks(
    confidence
):
    """
    Property 16: Manual Review Tasks Not Auto-Scheduled

    For any task marked as manual_review,
    no calendar blocks should be created.
    """
    orchestrator = get_orchestrator()
    mock_services = {
        'extraction': orchestrator.extraction,
        'post_processing': orchestrator.post_processing,
        'calendar': orchestrator.calendar,
        'meeting_prep': orchestrator.meeting_prep,
    }

    # Setup mocks
    mock_services['extraction'].extract_tasks.return_value = [
        {
            "id": "task-001",
            "title": "Test Task",
            "description": "Test Description",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": "test@example.com",
            "confidence": confidence,
            "priority": "medium",
            "state": "manual_review",
            "source_snippet": "Test",
        }
    ]

    mock_services['post_processing'].process_tasks.return_value = [
        {
            "id": "task-001",
            "title": "Test Task",
            "description": "Test Description",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": "test@example.com",
            "confidence": confidence,
            "priority": "medium",
            "state": "manual_review",
            "source_snippet": "Test",
        }
    ]

    mock_services['calendar'].find_slot_and_create_block.return_value = ("event-123", None)
    mock_services['meeting_prep'].detect_and_generate_prep.return_value = None

    from src.models.models import RunAgentRequestModel, EmailContentModel
    request = RunAgentRequestModel(
        email_content=EmailContentModel(
            subject="Test",
            body="Test",
            sender="test@example.com",
            timestamp="2024-03-15T10:00:00Z",
        ),
        user_timezone="America/New_York",
        calendar_id="primary",
    )

    response = orchestrator.run_agent(request)

    assert response.stats.calendar_blocks_created == 0
    assert response.tasks[0].calendar_block_id is None


@given(
    confidence=st.floats(min_value=0.0, max_value=0.69),
)
@settings(max_examples=100)
def test_property_16_manual_review_tasks_have_no_calendar_block_id(
    confidence
):
    """
    Property 16: Manual Review Tasks Not Auto-Scheduled

    For any task marked as manual_review,
    the calendar_block_id should be None.
    """
    orchestrator = get_orchestrator()
    mock_services = {
        'extraction': orchestrator.extraction,
        'post_processing': orchestrator.post_processing,
        'calendar': orchestrator.calendar,
        'meeting_prep': orchestrator.meeting_prep,
    }

    # Setup mocks
    mock_services['extraction'].extract_tasks.return_value = [
        {
            "id": "task-001",
            "title": "Test Task",
            "description": "Test Description",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": "test@example.com",
            "confidence": confidence,
            "priority": "medium",
            "state": "manual_review",
            "source_snippet": "Test",
        }
    ]

    mock_services['post_processing'].process_tasks.return_value = [
        {
            "id": "task-001",
            "title": "Test Task",
            "description": "Test Description",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": "test@example.com",
            "confidence": confidence,
            "priority": "medium",
            "state": "manual_review",
            "source_snippet": "Test",
        }
    ]

    mock_services['calendar'].find_slot_and_create_block.return_value = ("event-123", None)
    mock_services['meeting_prep'].detect_and_generate_prep.return_value = None

    from src.models.models import RunAgentRequestModel, EmailContentModel
    request = RunAgentRequestModel(
        email_content=EmailContentModel(
            subject="Test",
            body="Test",
            sender="test@example.com",
            timestamp="2024-03-15T10:00:00Z",
        ),
        user_timezone="America/New_York",
        calendar_id="primary",
    )

    response = orchestrator.run_agent(request)

    assert response.tasks[0].calendar_block_id is None
