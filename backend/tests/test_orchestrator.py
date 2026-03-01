"""Tests for orchestrator service."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from datetime import datetime
from unittest.mock import Mock

from backend.models.models import (
    EmailContentModel,
    RunAgentRequestModel,
    RunAgentResponseModel,
    FeedbackStatsModel,
    LogEntryModel,
    ErrorDetailModel,
)
from backend.src.services.orchestrator import AgentOrchestrator


class TestAgentOrchestrator:
    """Tests for AgentOrchestrator."""

    @pytest.fixture
    def mock_services(self):
        """Mock all services."""
        return {
            'extraction': Mock(),
            'post_processing': Mock(),
            'calendar': Mock(),
            'meeting_prep': Mock(),
        }

    @pytest.fixture
    def orchestrator(self, mock_services):
        """Orchestrator with mock services."""
        return AgentOrchestrator(
            extraction_service=mock_services['extraction'],
            post_processing_service=mock_services['post_processing'],
            calendar_service=mock_services['calendar'],
            meeting_prep_service=mock_services['meeting_prep'],
        )

    def test_run_agent_success(self, orchestrator, mock_services):
        """Test successful agent execution."""
        # Setup mocks
        mock_services['extraction'].extract_tasks.return_value = [
            {
                "id": "task-001",
                "title": "Project Meeting",
                "description": "Discuss project timeline",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": "john@example.com",
                "confidence": 0.9,
                "priority": "high",
                "state": "scheduled",
                "source_snippet": "Let's schedule a meeting.",
            }
        ]

        mock_services['post_processing'].process_tasks.return_value = [
            {
                "id": "task-001",
                "title": "Project Meeting",
                "description": "Discuss project timeline",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": "john@example.com",
                "confidence": 0.9,
                "priority": "high",
                "state": "scheduled",
                "source_snippet": "Let's schedule a meeting.",
            }
        ]

        mock_services['calendar'].find_slot_and_create_block.return_value = ("event-123", None)

        mock_services['meeting_prep'].detect_and_generate_prep.return_value = None

        request = RunAgentRequestModel(
            email_content=EmailContentModel(
                subject="Test Subject",
                body="Test Body",
                sender="test@example.com",
                timestamp="2024-03-15T10:00:00Z",
            ),
            user_timezone="America/New_York",
            calendar_id="primary",
        )

        response = orchestrator.run_agent(request)

        assert isinstance(response, RunAgentResponseModel)
        assert len(response.tasks) == 1
        assert response.stats.tasks_extracted == 1
        assert response.stats.calendar_blocks_created == 1

    def test_run_agent_manual_review(self, orchestrator, mock_services):
        """Test agent execution with manual review task."""
        # Setup mocks
        mock_services['extraction'].extract_tasks.return_value = [
            {
                "id": "task-001",
                "title": "Project Meeting",
                "description": "Discuss project timeline",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": "john@example.com",
                "confidence": 0.6,  # Below threshold
                "priority": "high",
                "state": "manual_review",
                "source_snippet": "Let's schedule a meeting.",
            }
        ]

        mock_services['post_processing'].process_tasks.return_value = [
            {
                "id": "task-001",
                "title": "Project Meeting",
                "description": "Discuss project timeline",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": "john@example.com",
                "confidence": 0.6,
                "priority": "high",
                "state": "manual_review",
                "source_snippet": "Let's schedule a meeting.",
            }
        ]

        mock_services['calendar'].find_slot_and_create_block.return_value = (None, None)

        mock_services['meeting_prep'].detect_and_generate_prep.return_value = None

        request = RunAgentRequestModel(
            email_content=EmailContentModel(
                subject="Test Subject",
                body="Test Body",
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

    def test_run_agent_scheduling_conflict(self, orchestrator, mock_services):
        """Test agent execution with scheduling conflict."""
        # Setup mocks
        mock_services['extraction'].extract_tasks.return_value = [
            {
                "id": "task-001",
                "title": "Project Meeting",
                "description": "Discuss project timeline",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": "john@example.com",
                "confidence": 0.9,
                "priority": "high",
                "state": "scheduled",
                "source_snippet": "Let's schedule a meeting.",
            }
        ]

        mock_services['post_processing'].process_tasks.return_value = [
            {
                "id": "task-001",
                "title": "Project Meeting",
                "description": "Discuss project timeline",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": "john@example.com",
                "confidence": 0.9,
                "priority": "high",
                "state": "scheduled",
                "source_snippet": "Let's schedule a meeting.",
            }
        ]

        mock_services['calendar'].find_slot_and_create_block.return_value = (None, "scheduling_conflict")

        mock_services['meeting_prep'].detect_and_generate_prep.return_value = None

        request = RunAgentRequestModel(
            email_content=EmailContentModel(
                subject="Test Subject",
                body="Test Body",
                sender="test@example.com",
                timestamp="2024-03-15T10:00:00Z",
            ),
            user_timezone="America/New_York",
            calendar_id="primary",
        )

        response = orchestrator.run_agent(request)

        assert len(response.tasks) == 1
        assert response.tasks[0].state == "scheduling_conflict"
        assert response.stats.scheduling_conflicts == 1

    def test_run_agent_meeting_prep(self, orchestrator, mock_services):
        """Test agent execution with meeting prep generation."""
        from src.models.models import MeetingPrepDocument

        # Setup mocks
        mock_services['extraction'].extract_tasks.return_value = [
            {
                "id": "task-001",
                "title": "Project Meeting",
                "description": "Discuss project timeline",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": "john@example.com",
                "confidence": 0.9,
                "priority": "high",
                "state": "scheduled",
                "source_snippet": "Let's schedule a meeting.",
            }
        ]

        mock_services['post_processing'].process_tasks.return_value = [
            {
                "id": "task-001",
                "title": "Project Meeting",
                "description": "Discuss project timeline",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": "john@example.com",
                "confidence": 0.9,
                "priority": "high",
                "state": "scheduled",
                "source_snippet": "Let's schedule a meeting.",
            }
        ]

        mock_services['calendar'].find_slot_and_create_block.return_value = ("event-123", None)

        mock_services['meeting_prep'].detect_and_generate_prep.return_value = MeetingPrepDocument(
            meeting_title="Project Meeting",
            meeting_time=datetime(2024, 3, 20, 14, 0, 0),
            context_summary="Meeting to discuss project timeline.",
            talking_points=["Timeline", "Milestones"],
            questions=["What is the deadline?"],
            risks=["Timeline slippage"],
        )

        request = RunAgentRequestModel(
            email_content=EmailContentModel(
                subject="Test Subject",
                body="Test Body",
                sender="test@example.com",
                timestamp="2024-03-15T10:00:00Z",
            ),
            user_timezone="America/New_York",
            calendar_id="primary",
        )

        response = orchestrator.run_agent(request)

        assert len(response.tasks) == 1
        # meeting_prep is added to task dict but not to TaskModel
        # The test verifies that meeting prep was generated
        assert mock_services['meeting_prep'].detect_and_generate_prep.called

    def test_run_agent_extraction_error(self, orchestrator, mock_services):
        """Test agent execution with extraction error."""
        from backend.src.services.extraction import ExtractionError

        # Setup mocks - extraction fails
        mock_services['extraction'].extract_tasks.side_effect = ExtractionError("Failed to extract tasks")

        request = RunAgentRequestModel(
            email_content=EmailContentModel(
                subject="Test Subject",
                body="Test Body",
                sender="test@example.com",
                timestamp="2024-03-15T10:00:00Z",
            ),
            user_timezone="America/New_York",
            calendar_id="primary",
        )

        response = orchestrator.run_agent(request)

        # Should return empty tasks with error
        assert len(response.tasks) == 0
        assert len(response.errors) == 1
        assert response.errors[0].code == "EXTRACTION_ERROR"
        assert "Failed to extract tasks" in response.errors[0].message

    def test_run_agent_general_error(self, orchestrator, mock_services):
        """Test agent execution with general error."""
        # Setup mocks - post-processing fails
        mock_services['extraction'].extract_tasks.return_value = [
            {
                "id": "task-001",
                "title": "Project Meeting",
                "description": "Discuss project timeline",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": "john@example.com",
                "confidence": 0.9,
                "priority": "high",
                "state": "scheduled",
                "source_snippet": "Let's schedule a meeting.",
            }
        ]

        mock_services['post_processing'].process_tasks.side_effect = Exception("Unexpected error")

        request = RunAgentRequestModel(
            email_content=EmailContentModel(
                subject="Test Subject",
                body="Test Body",
                sender="test@example.com",
                timestamp="2024-03-15T10:00:00Z",
            ),
            user_timezone="America/New_York",
            calendar_id="primary",
        )

        response = orchestrator.run_agent(request)

        # Should return empty tasks with error
        assert len(response.tasks) == 0
        assert len(response.errors) == 1
        assert response.errors[0].code == "AGENT_EXECUTION_ERROR"
        assert "Unexpected error" in response.errors[0].message

    def test_run_agent_multiple_tasks_graceful_degradation(self, orchestrator, mock_services):
        """Test agent execution with multiple tasks where one fails."""
        # Setup mocks with multiple tasks
        mock_services['extraction'].extract_tasks.return_value = [
            {
                "id": "task-001",
                "title": "Project Meeting",
                "description": "Discuss project timeline",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": "john@example.com",
                "confidence": 0.9,
                "priority": "high",
                "state": "scheduled",
                "source_snippet": "Let's schedule a meeting.",
            },
            {
                "id": "task-002",
                "title": "Code Review",
                "description": "Review pull request",
                "deadline": datetime(2024, 3, 21, 10, 0, 0),
                "owner": "jane@example.com",
                "confidence": 0.8,
                "priority": "medium",
                "state": "scheduled",
                "source_snippet": "Please review the PR.",
            }
        ]

        mock_services['post_processing'].process_tasks.return_value = [
            {
                "id": "task-001",
                "title": "Project Meeting",
                "description": "Discuss project timeline",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": "john@example.com",
                "confidence": 0.9,
                "priority": "high",
                "state": "scheduled",
                "source_snippet": "Let's schedule a meeting.",
            },
            {
                "id": "task-002",
                "title": "Code Review",
                "description": "Review pull request",
                "deadline": datetime(2024, 3, 21, 10, 0, 0),
                "owner": "jane@example.com",
                "confidence": 0.8,
                "priority": "medium",
                "state": "scheduled",
                "source_snippet": "Please review the PR.",
            }
        ]

        # First task succeeds, second has scheduling conflict
        def calendar_side_effect(task, calendar_id):
            if task['id'] == 'task-001':
                return ("event-123", None)
            else:
                return (None, "scheduling_conflict")

        mock_services['calendar'].find_slot_and_create_block.side_effect = calendar_side_effect
        mock_services['meeting_prep'].detect_and_generate_prep.return_value = None

        request = RunAgentRequestModel(
            email_content=EmailContentModel(
                subject="Test Subject",
                body="Test Body",
                sender="test@example.com",
                timestamp="2024-03-15T10:00:00Z",
            ),
            user_timezone="America/New_York",
            calendar_id="primary",
        )

        response = orchestrator.run_agent(request)

        # Both tasks should be returned with different states
        assert len(response.tasks) == 2
        assert response.tasks[0].state == "scheduled"
        assert response.tasks[1].state == "scheduling_conflict"
        assert response.stats.calendar_blocks_created == 1
        assert response.stats.scheduling_conflicts == 1

    def test_run_agent_logs_execution_steps(self, orchestrator, mock_services):
        """Test that agent logs execution steps."""
        # Setup mocks
        mock_services['extraction'].extract_tasks.return_value = [
            {
                "id": "task-001",
                "title": "Project Meeting",
                "description": "Discuss project timeline",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": "john@example.com",
                "confidence": 0.9,
                "priority": "high",
                "state": "scheduled",
                "source_snippet": "Let's schedule a meeting.",
            }
        ]

        mock_services['post_processing'].process_tasks.return_value = [
            {
                "id": "task-001",
                "title": "Project Meeting",
                "description": "Discuss project timeline",
                "deadline": datetime(2024, 3, 20, 14, 0, 0),
                "owner": "john@example.com",
                "confidence": 0.9,
                "priority": "high",
                "state": "scheduled",
                "source_snippet": "Let's schedule a meeting.",
            }
        ]

        mock_services['calendar'].find_slot_and_create_block.return_value = ("event-123", None)
        mock_services['meeting_prep'].detect_and_generate_prep.return_value = None

        request = RunAgentRequestModel(
            email_content=EmailContentModel(
                subject="Test Subject",
                body="Test Body",
                sender="test@example.com",
                timestamp="2024-03-15T10:00:00Z",
            ),
            user_timezone="America/New_York",
            calendar_id="primary",
        )

        response = orchestrator.run_agent(request)

        # Should have logs for each step
        assert len(response.logs) >= 3
        log_messages = [log.message for log in response.logs]
        assert any("Extracting tasks" in msg for msg in log_messages)
        assert any("Post-processing tasks" in msg for msg in log_messages)
        assert any("Created calendar block" in msg for msg in log_messages)
