"""Property-based tests for feedback stats accuracy."""

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
    task_count=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=100)
def test_property_21_tasks_extracted_count_is_accurate(
    task_count
):
    """
    Property 21: Feedback Stats Accuracy

    For any agent execution,
    the tasks_extracted count should match the actual number of tasks extracted.
    """
    orchestrator = get_orchestrator()
    mock_services = {
        'extraction': orchestrator.extraction,
        'post_processing': orchestrator.post_processing,
        'calendar': orchestrator.calendar,
        'meeting_prep': orchestrator.meeting_prep,
    }

    # Setup mocks
    tasks = []
    for i in range(task_count):
        tasks.append({
            "id": f"task-{i}",
            "title": f"Task {i}",
            "description": f"Description {i}",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": f"user{i}@example.com",
            "confidence": 0.9,
            "priority": "medium",
            "state": "scheduled",
            "source_snippet": f"Source {i}",
        })

    mock_services['extraction'].extract_tasks.return_value = tasks
    mock_services['post_processing'].process_tasks.return_value = tasks
    mock_services['calendar'].find_slot_and_create_block.return_value = (f"event-123", None)
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

    assert response.stats.tasks_extracted == task_count


@given(
    scheduled_count=st.integers(min_value=0, max_value=5),
    conflict_count=st.integers(min_value=0, max_value=5),
    review_count=st.integers(min_value=0, max_value=5),
)
@settings(max_examples=100)
def test_property_21_calendar_blocks_created_count_is_accurate(
    scheduled_count, conflict_count, review_count
):
    """
    Property 21: Feedback Stats Accuracy

    For any agent execution,
    the calendar_blocks_created count should match the actual number of blocks created.
    """
    orchestrator = get_orchestrator()
    mock_services = {
        'extraction': orchestrator.extraction,
        'post_processing': orchestrator.post_processing,
        'calendar': orchestrator.calendar,
        'meeting_prep': orchestrator.meeting_prep,
    }

    # Setup mocks
    tasks = []
    for i in range(scheduled_count):
        tasks.append({
            "id": f"task-{i}",
            "title": f"Task {i}",
            "description": f"Description {i}",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": f"user{i}@example.com",
            "confidence": 0.9,
            "priority": "medium",
            "state": "scheduled",
            "source_snippet": f"Source {i}",
        })

    for i in range(conflict_count):
        tasks.append({
            "id": f"conflict-{i}",
            "title": f"Conflict {i}",
            "description": f"Description {i}",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": f"user{i}@example.com",
            "confidence": 0.9,
            "priority": "medium",
            "state": "scheduling_conflict",
            "source_snippet": f"Source {i}",
        })

    for i in range(review_count):
        tasks.append({
            "id": f"review-{i}",
            "title": f"Review {i}",
            "description": f"Description {i}",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": f"user{i}@example.com",
            "confidence": 0.5,
            "priority": "medium",
            "state": "manual_review",
            "source_snippet": f"Source {i}",
        })

    mock_services['extraction'].extract_tasks.return_value = tasks
    mock_services['post_processing'].process_tasks.return_value = tasks

    # Only scheduled tasks get calendar blocks
    def find_slot_side_effect(task, calendar_id):
        if "scheduled" in task.get("state", ""):
            return (f"event-{task['id']}", None)
        return (None, "scheduling_conflict" if "conflict" in task.get("id", "") else None)

    mock_services['calendar'].find_slot_and_create_block.side_effect = find_slot_side_effect
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

    assert response.stats.calendar_blocks_created == scheduled_count


@given(
    scheduled_count=st.integers(min_value=0, max_value=5),
    conflict_count=st.integers(min_value=0, max_value=5),
    review_count=st.integers(min_value=0, max_value=5),
)
@settings(max_examples=100)
def test_property_21_scheduling_conflicts_count_is_accurate(
    scheduled_count, conflict_count, review_count
):
    """
    Property 21: Feedback Stats Accuracy

    For any agent execution,
    the scheduling_conflicts count should match the actual number of conflicts.
    """
    orchestrator = get_orchestrator()
    mock_services = {
        'extraction': orchestrator.extraction,
        'post_processing': orchestrator.post_processing,
        'calendar': orchestrator.calendar,
        'meeting_prep': orchestrator.meeting_prep,
    }

    # Setup mocks
    tasks = []
    for i in range(scheduled_count):
        tasks.append({
            "id": f"task-{i}",
            "title": f"Task {i}",
            "description": f"Description {i}",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": f"user{i}@example.com",
            "confidence": 0.9,
            "priority": "medium",
            "state": "scheduled",
            "source_snippet": f"Source {i}",
        })

    for i in range(conflict_count):
        tasks.append({
            "id": f"conflict-{i}",
            "title": f"Conflict {i}",
            "description": f"Description {i}",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": f"user{i}@example.com",
            "confidence": 0.9,
            "priority": "medium",
            "state": "scheduling_conflict",
            "source_snippet": f"Source {i}",
        })

    for i in range(review_count):
        tasks.append({
            "id": f"review-{i}",
            "title": f"Review {i}",
            "description": f"Description {i}",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": f"user{i}@example.com",
            "confidence": 0.5,
            "priority": "medium",
            "state": "manual_review",
            "source_snippet": f"Source {i}",
        })

    mock_services['extraction'].extract_tasks.return_value = tasks
    mock_services['post_processing'].process_tasks.return_value = tasks

    # Only scheduled tasks get calendar blocks
    def find_slot_side_effect(task, calendar_id):
        if "scheduled" in task.get("state", ""):
            return (f"event-{task['id']}", None)
        return (None, "scheduling_conflict" if "conflict" in task.get("id", "") else None)

    mock_services['calendar'].find_slot_and_create_block.side_effect = find_slot_side_effect
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

    assert response.stats.scheduling_conflicts == conflict_count


@given(
    scheduled_count=st.integers(min_value=0, max_value=5),
    conflict_count=st.integers(min_value=0, max_value=5),
    review_count=st.integers(min_value=0, max_value=5),
)
@settings(max_examples=100)
def test_property_21_manual_review_items_count_is_accurate(
    scheduled_count, conflict_count, review_count
):
    """
    Property 21: Feedback Stats Accuracy

    For any agent execution,
    the manual_review_items count should match the actual number of manual review items.
    """
    orchestrator = get_orchestrator()
    mock_services = {
        'extraction': orchestrator.extraction,
        'post_processing': orchestrator.post_processing,
        'calendar': orchestrator.calendar,
        'meeting_prep': orchestrator.meeting_prep,
    }

    # Setup mocks
    tasks = []
    for i in range(scheduled_count):
        tasks.append({
            "id": f"task-{i}",
            "title": f"Task {i}",
            "description": f"Description {i}",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": f"user{i}@example.com",
            "confidence": 0.9,
            "priority": "medium",
            "state": "scheduled",
            "source_snippet": f"Source {i}",
        })

    for i in range(conflict_count):
        tasks.append({
            "id": f"conflict-{i}",
            "title": f"Conflict {i}",
            "description": f"Description {i}",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": f"user{i}@example.com",
            "confidence": 0.9,
            "priority": "medium",
            "state": "scheduling_conflict",
            "source_snippet": f"Source {i}",
        })

    for i in range(review_count):
        tasks.append({
            "id": f"review-{i}",
            "title": f"Review {i}",
            "description": f"Description {i}",
            "deadline": datetime(2024, 3, 20, 14, 0, 0),
            "owner": f"user{i}@example.com",
            "confidence": 0.5,
            "priority": "medium",
            "state": "manual_review",
            "source_snippet": f"Source {i}",
        })

    mock_services['extraction'].extract_tasks.return_value = tasks
    mock_services['post_processing'].process_tasks.return_value = tasks

    # Only scheduled tasks get calendar blocks
    def find_slot_side_effect(task, calendar_id):
        if "scheduled" in task.get("state", ""):
            return (f"event-{task['id']}", None)
        return (None, "scheduling_conflict" if "conflict" in task.get("id", "") else None)

    mock_services['calendar'].find_slot_and_create_block.side_effect = find_slot_side_effect
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

    assert response.stats.manual_review_items == review_count
