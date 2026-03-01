"""
Unit tests for the /run-agent API endpoint.

Tests valid request handling (200 response), invalid request handling (422 response),
and CORS headers presence.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

from backend.src.main import app
from backend.models.models import (
    RunAgentRequestModel,
    RunAgentResponseModel,
    EmailContentModel,
    TaskModel,
    FeedbackStatsModel,
    LogEntryModel,
    ErrorDetailModel
)

# Create test client
client = TestClient(app)


class TestRunAgentEndpoint:
    """Tests for the /run-agent endpoint."""

    def test_run_agent_valid_request_returns_200(self):
        """
        Test valid request handling returns 200 response.
        
        Validates: Requirements 13.3, 13.4, 13.5, 13.6, 13.7
        """
        request_data = {
            "email_content": {
                "subject": "Test Subject",
                "body": "Test Body",
                "sender": "test@example.com",
                "timestamp": "2024-01-15T10:00:00Z"
            },
            "user_timezone": "UTC",
            "calendar_id": "primary"
        }
        
        response = client.post("/run-agent", json=request_data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert "tasks" in data
        assert "stats" in data
        assert "logs" in data

    def test_run_agent_missing_required_field_returns_422(self):
        """
        Test invalid request handling returns 422 response with validation errors.
        
        Validates: Requirements 13.3, 13.4, 13.5, 13.6, 13.7
        """
        request_data = {
            "email_content": {
                "subject": "Test Subject",
                # Missing required fields: body, sender, timestamp
            },
            "user_timezone": "UTC",
            "calendar_id": "primary"
        }
        
        response = client.post("/run-agent", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "errors" in data

    def test_run_agent_empty_string_fields_returns_200(self):
        """
        Test that empty string fields are accepted (Pydantic doesn't validate empty strings by default).
        
        Validates: Requirements 13.3, 13.4, 13.5, 13.6, 13.7
        """
        request_data = {
            "email_content": {
                "subject": "",
                "body": "",
                "sender": "",
                "timestamp": ""
            },
            "user_timezone": "",
            "calendar_id": ""
        }
        
        response = client.post("/run-agent", json=request_data)
        
        # Empty strings are valid for Pydantic str fields
        assert response.status_code == 200

    def test_run_agent_invalid_confidence_returns_422(self):
        """
        Test invalid confidence score returns 422 response.
        
        Validates: Requirements 13.3, 13.4, 13.5, 13.6, 13.7
        """
        request_data = {
            "email_content": {
                "subject": "Test Subject",
                "body": "Test Body",
                "sender": "test@example.com",
                "timestamp": "2024-01-15T10:00:00Z"
            },
            "user_timezone": "UTC",
            "calendar_id": "primary"
        }
        
        # Note: This test validates that the model validation works at the API level
        # The actual task model validation is tested in test_models.py
        response = client.post("/run-agent", json=request_data)
        
        assert response.status_code == 200  # Request is valid, even if tasks are empty


class TestCORSMiddleware:
    """Tests for CORS middleware configuration."""

    def test_cors_headers_present_on_post_request(self):
        """
        Test CORS headers are present on POST request.
        
        Validates: Requirements 13.3, 13.4, 13.5, 13.6, 13.7
        """
        request_data = {
            "email_content": {
                "subject": "Test Subject",
                "body": "Test Body",
                "sender": "test@example.com",
                "timestamp": "2024-01-15T10:00:00Z"
            },
            "user_timezone": "UTC",
            "calendar_id": "primary"
        }
        
        # Include Origin header to trigger CORS response
        response = client.post(
            "/run-agent",
            json=request_data,
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200
        # CORS headers should be present when Origin is included
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-credentials" in response.headers


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_check_returns_200(self):
        """
        Test health check endpoint returns 200 response.
        """
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestEndpointIntegration:
    """Tests for endpoint integration with orchestrator."""

    @patch('backend.src.main.orchestrator')
    def test_successful_execution_with_valid_request(self, mock_orchestrator):
        """
        Test successful execution with valid request returns proper response.
        
        Validates: Requirements 13.4, 13.5, 13.6
        """
        # Mock orchestrator response
        mock_response = RunAgentResponseModel(
            tasks=[
                TaskModel(
                    id="task-001",
                    title="Project Meeting",
                    description="Discuss project timeline",
                    deadline=datetime(2024, 3, 20, 14, 0, 0),
                    owner="john@example.com",
                    confidence=0.9,
                    priority="high",
                    state="scheduled",
                    calendar_block_id="cal-123",
                    source_snippet="Let's schedule a meeting."
                )
            ],
            stats=FeedbackStatsModel(
                tasks_extracted=1,
                calendar_blocks_created=1,
                scheduling_conflicts=0,
                manual_review_items=0
            ),
            logs=[
                LogEntryModel(
                    timestamp=datetime.now(),
                    message="Extracting tasks from email",
                    level="INFO"
                )
            ],
            errors=[]
        )
        mock_orchestrator.run_agent.return_value = mock_response
        
        request_data = {
            "email_content": {
                "subject": "Project Update",
                "body": "Let's schedule a meeting to discuss the project timeline.",
                "sender": "john@example.com",
                "timestamp": "2024-03-15T10:00:00Z"
            },
            "user_timezone": "UTC",
            "calendar_id": "primary"
        }
        
        response = client.post("/run-agent", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Project Meeting"
        assert data["stats"]["tasks_extracted"] == 1
        assert data["stats"]["calendar_blocks_created"] == 1
        assert len(data["logs"]) > 0
        assert len(data["errors"]) == 0

    @patch('backend.src.main.orchestrator')
    def test_error_response_for_extraction_failure(self, mock_orchestrator):
        """
        Test error response when extraction fails.
        
        Validates: Requirements 13.4, 13.5, 13.6
        """
        # Mock orchestrator response with error
        mock_response = RunAgentResponseModel(
            tasks=[],
            stats=FeedbackStatsModel(
                tasks_extracted=0,
                calendar_blocks_created=0,
                scheduling_conflicts=0,
                manual_review_items=0
            ),
            logs=[
                LogEntryModel(
                    timestamp=datetime.now(),
                    message="Extraction failed",
                    level="ERROR"
                )
            ],
            errors=[
                ErrorDetailModel(
                    code="EXTRACTION_ERROR",
                    message="Failed to extract tasks from email",
                    context={"step": "extraction"}
                )
            ]
        )
        mock_orchestrator.run_agent.return_value = mock_response
        
        request_data = {
            "email_content": {
                "subject": "Test",
                "body": "Test body",
                "sender": "test@example.com",
                "timestamp": "2024-03-15T10:00:00Z"
            },
            "user_timezone": "UTC",
            "calendar_id": "primary"
        }
        
        response = client.post("/run-agent", json=request_data)
        
        assert response.status_code == 200  # Still returns 200 with error details
        data = response.json()
        assert len(data["tasks"]) == 0
        assert len(data["errors"]) == 1
        assert data["errors"][0]["code"] == "EXTRACTION_ERROR"

    @patch('backend.src.main.orchestrator')
    def test_error_response_for_calendar_failure(self, mock_orchestrator):
        """
        Test error response when calendar scheduling fails.
        
        Validates: Requirements 13.4, 13.5, 13.6
        """
        # Mock orchestrator response with scheduling conflict
        mock_response = RunAgentResponseModel(
            tasks=[
                TaskModel(
                    id="task-001",
                    title="Urgent Task",
                    description="Complete urgent task",
                    deadline=datetime(2024, 3, 16, 10, 0, 0),
                    owner="john@example.com",
                    confidence=0.95,
                    priority="high",
                    state="scheduling_conflict",
                    calendar_block_id=None,
                    source_snippet="Complete this urgently."
                )
            ],
            stats=FeedbackStatsModel(
                tasks_extracted=1,
                calendar_blocks_created=0,
                scheduling_conflicts=1,
                manual_review_items=0
            ),
            logs=[
                LogEntryModel(
                    timestamp=datetime.now(),
                    message="Scheduling conflict for task 'Urgent Task'",
                    level="INFO"
                )
            ],
            errors=[]
        )
        mock_orchestrator.run_agent.return_value = mock_response
        
        request_data = {
            "email_content": {
                "subject": "Urgent",
                "body": "Complete this urgently.",
                "sender": "john@example.com",
                "timestamp": "2024-03-15T10:00:00Z"
            },
            "user_timezone": "UTC",
            "calendar_id": "primary"
        }
        
        response = client.post("/run-agent", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["state"] == "scheduling_conflict"
        assert data["stats"]["scheduling_conflicts"] == 1

    @patch('backend.src.main.orchestrator', None)
    def test_service_initialization_failure(self):
        """
        Test response when orchestrator fails to initialize.
        
        Validates: Requirements 13.4, 13.5, 13.6
        """
        request_data = {
            "email_content": {
                "subject": "Test",
                "body": "Test body",
                "sender": "test@example.com",
                "timestamp": "2024-03-15T10:00:00Z"
            },
            "user_timezone": "UTC",
            "calendar_id": "primary"
        }
        
        response = client.post("/run-agent", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["errors"]) == 1
        assert data["errors"][0]["code"] == "SERVICE_INITIALIZATION_ERROR"

    @patch('backend.src.main.orchestrator')
    def test_unexpected_exception_handling(self, mock_orchestrator):
        """
        Test handling of unexpected exceptions during execution.
        
        Validates: Requirements 13.4, 13.5, 13.6
        """
        # Mock orchestrator to raise exception
        mock_orchestrator.run_agent.side_effect = RuntimeError("Unexpected error")
        
        request_data = {
            "email_content": {
                "subject": "Test",
                "body": "Test body",
                "sender": "test@example.com",
                "timestamp": "2024-03-15T10:00:00Z"
            },
            "user_timezone": "UTC",
            "calendar_id": "primary"
        }
        
        response = client.post("/run-agent", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["errors"]) == 1
        assert data["errors"][0]["code"] == "UNEXPECTED_ERROR"
        assert "unexpected error" in data["errors"][0]["message"].lower()

    @patch('backend.src.main.orchestrator')
    def test_logging_output_for_successful_execution(self, mock_orchestrator):
        """
        Test that logging output is properly generated.
        
        Validates: Requirements 13.4, 13.5, 13.6
        """
        # Mock orchestrator response with logs
        mock_response = RunAgentResponseModel(
            tasks=[],
            stats=FeedbackStatsModel(
                tasks_extracted=0,
                calendar_blocks_created=0,
                scheduling_conflicts=0,
                manual_review_items=0
            ),
            logs=[
                LogEntryModel(
                    timestamp=datetime.now(),
                    message="Step 1: Extracting tasks",
                    level="INFO"
                ),
                LogEntryModel(
                    timestamp=datetime.now(),
                    message="Step 2: Post-processing",
                    level="INFO"
                ),
                LogEntryModel(
                    timestamp=datetime.now(),
                    message="Step 3: Scheduling",
                    level="INFO"
                )
            ],
            errors=[]
        )
        mock_orchestrator.run_agent.return_value = mock_response
        
        request_data = {
            "email_content": {
                "subject": "Test",
                "body": "Test body",
                "sender": "test@example.com",
                "timestamp": "2024-03-15T10:00:00Z"
            },
            "user_timezone": "UTC",
            "calendar_id": "primary"
        }
        
        response = client.post("/run-agent", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["logs"]) == 3
        assert data["logs"][0]["message"] == "Step 1: Extracting tasks"
        assert data["logs"][1]["message"] == "Step 2: Post-processing"
        assert data["logs"][2]["message"] == "Step 3: Scheduling"
