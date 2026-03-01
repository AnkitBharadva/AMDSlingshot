"""Property-based tests for manual review threshold."""

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
def test_property_15_confidence_below_threshold_marked_manual_review(
    confidence
):
    """
    Property 15: Low Confidence Manual Review Threshold

    For any task with confidence below 0.7,
    the task should be marked as manual_review.
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

    mock_services['calendar'].find_slot_and_create_block.return_value = (None, None)
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

    assert len(response.tasks) == 1
    assert response.tasks[0].state == "manual_review"
    assert response.stats.manual_review_items == 1


@given(
    confidence=st.floats(min_value=0.7, max_value=1.0),
)
@settings(max_examples=100)
def test_property_15_confidence_at_or_above_threshold_not_manual_review(
    confidence
):
    """
    Property 15: Low Confidence Manual Review Threshold

    For any task with confidence at or above 0.7,
    the task should NOT be marked as manual_review.
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
            "state": "scheduled",
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
            "state": "scheduled",
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

    assert len(response.tasks) == 1
    assert response.tasks[0].state != "manual_review"
    assert response.stats.manual_review_items == 0


@given(
    confidence=st.floats(min_value=0.0, max_value=0.69),
)
@settings(max_examples=100)
def test_property_15_manual_review_tasks_not_auto_scheduled(
    confidence
):
    """
    Property 15: Low Confidence Manual Review Threshold

    For any task marked as manual_review,
    no calendar block should be created.
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

    mock_services['calendar'].find_slot_and_create_block.return_value = (None, None)
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
    assert response.stats.calendar_blocks_created == 0
