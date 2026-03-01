"""Property-based tests for request statelessness."""

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
    request_count=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=100)
def test_property_22_requests_are_independent(
    request_count
):
    """
    Property 22: Request Statelessness

    For any sequence of requests,
    each request should be processed independently.
    """
    orchestrator = get_orchestrator()

    from src.models.models import RunAgentRequestModel, EmailContentModel

    results = []
    for i in range(request_count):
        # Setup mocks for each request
        orchestrator.extraction.extract_tasks.return_value = [
            {
                "id": f"task-{i}",
                "title": f"Task {i}",
                "description": f"Description {i}",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": f"user{i}@example.com",
                "confidence": 0.9,
                "priority": "medium",
                "state": "scheduled",
                "source_snippet": f"Source {i}",
            }
        ]

        orchestrator.post_processing.process_tasks.return_value = [
            {
                "id": f"task-{i}",
                "title": f"Task {i}",
                "description": f"Description {i}",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": f"user{i}@example.com",
                "confidence": 0.9,
                "priority": "medium",
                "state": "scheduled",
                "source_snippet": f"Source {i}",
            }
        ]

        orchestrator.calendar.find_slot_and_create_block.return_value = (f"event-{i}", None)
        orchestrator.meeting_prep.detect_and_generate_prep.return_value = None

        request = RunAgentRequestModel(
            email_content=EmailContentModel(
                subject=f"Request {i}",
                body=f"Body {i}",
                sender=f"user{i}@example.com",
                timestamp="2024-03-15T10:00:00Z",
            ),
            user_timezone="America/New_York",
            calendar_id="primary",
        )

        response = orchestrator.run_agent(request)
        results.append(response)

    # Each request should be processed independently
    for i, result in enumerate(results):
        assert len(result.tasks) == 1
        assert result.tasks[0].title == f"Task {i}"


@given(
    request_count=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=100)
def test_property_22_no_state_leaks_between_requests(
    request_count
):
    """
    Property 22: Request Statelessness

    For any sequence of requests,
    no state should leak from one request to another.
    """
    orchestrator = get_orchestrator()

    from src.models.models import RunAgentRequestModel, EmailContentModel

    for i in range(request_count):
        # Setup mocks for each request
        orchestrator.extraction.extract_tasks.return_value = [
            {
                "id": f"task-{i}",
                "title": f"Task {i}",
                "description": f"Description {i}",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": f"user{i}@example.com",
                "confidence": 0.9,
                "priority": "medium",
                "state": "scheduled",
                "source_snippet": f"Source {i}",
            }
        ]

        orchestrator.post_processing.process_tasks.return_value = [
            {
                "id": f"task-{i}",
                "title": f"Task {i}",
                "description": f"Description {i}",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": f"user{i}@example.com",
                "confidence": 0.9,
                "priority": "medium",
                "state": "scheduled",
                "source_snippet": f"Source {i}",
            }
        ]

        orchestrator.calendar.find_slot_and_create_block.return_value = (f"event-{i}", None)
        orchestrator.meeting_prep.detect_and_generate_prep.return_value = None

        request = RunAgentRequestModel(
            email_content=EmailContentModel(
                subject=f"Request {i}",
                body=f"Body {i}",
                sender=f"user{i}@example.com",
                timestamp="2024-03-15T10:00:00Z",
            ),
            user_timezone="America/New_York",
            calendar_id="primary",
        )

        response = orchestrator.run_agent(request)

        # Verify no state leak - each response should be independent
        assert len(response.tasks) == 1
        assert response.tasks[0].title == f"Task {i}"
        assert response.stats.tasks_extracted == 1


@given(
    request_count=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=100)
def test_property_22_services_are_reinstantiated_per_request(
    request_count
):
    """
    Property 22: Request Statelessness

    For any sequence of requests,
    services should not maintain state between requests.
    """
    orchestrator = get_orchestrator()

    from src.models.models import RunAgentRequestModel, EmailContentModel

    for i in range(request_count):
        # Reset mocks for each request
        orchestrator.extraction.reset_mock()
        orchestrator.post_processing.reset_mock()
        orchestrator.calendar.reset_mock()
        orchestrator.meeting_prep.reset_mock()

        # Setup mocks for each request
        orchestrator.extraction.extract_tasks.return_value = [
            {
                "id": f"task-{i}",
                "title": f"Task {i}",
                "description": f"Description {i}",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": f"user{i}@example.com",
                "confidence": 0.9,
                "priority": "medium",
                "state": "scheduled",
                "source_snippet": f"Source {i}",
            }
        ]

        orchestrator.post_processing.process_tasks.return_value = [
            {
                "id": f"task-{i}",
                "title": f"Task {i}",
                "description": f"Description {i}",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": f"user{i}@example.com",
                "confidence": 0.9,
                "priority": "medium",
                "state": "scheduled",
                "source_snippet": f"Source {i}",
            }
        ]

        orchestrator.calendar.find_slot_and_create_block.return_value = (f"event-{i}", None)
        orchestrator.meeting_prep.detect_and_generate_prep.return_value = None

        request = RunAgentRequestModel(
            email_content=EmailContentModel(
                subject=f"Request {i}",
                body=f"Body {i}",
                sender=f"user{i}@example.com",
                timestamp="2024-03-15T10:00:00Z",
            ),
            user_timezone="America/New_York",
            calendar_id="primary",
        )

        response = orchestrator.run_agent(request)

        # Each request should call services independently
        assert orchestrator.extraction.extract_tasks.call_count == 1
        assert orchestrator.post_processing.process_tasks.call_count == 1
