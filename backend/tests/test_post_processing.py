"""Tests for post-processing service."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from datetime import datetime, timedelta

from backend.src.services.post_processing import PostProcessingService


class TestPostProcessingService:
    """Tests for PostProcessingService."""

    @pytest.fixture
    def service(self):
        """Post-processing service instance."""
        return PostProcessingService()

    def test_assign_priority_high_urgent_keyword(self, service):
        """Test high priority assignment with urgent keyword."""
        task = {
            "title": "URGENT: Fix critical bug",
            "description": "Fix the production bug immediately",
            "deadline": datetime(2024, 3, 25, 17, 0, 0),
            "owner": "john@example.com",
            "confidence": 0.9,
            "source_snippet": "URGENT: Fix critical bug",
        }

        current_time = datetime(2024, 3, 20, 10, 0, 0)
        result = service._assign_priority(task, current_time)

        assert result["priority"] == "high"

    def test_assign_priority_high_deadline(self, service):
        """Test high priority assignment with deadline < 24 hours."""
        task = {
            "title": "Quick Review",
            "description": "Please review this quickly",
            "deadline": datetime.now() + timedelta(hours=12),
            "owner": "john@example.com",
            "confidence": 0.9,
            "source_snippet": "Quick review",
        }

        current_time = datetime.now()
        result = service._assign_priority(task, current_time)

        assert result["priority"] == "high"

    def test_assign_priority_medium_default(self, service):
        """Test medium priority assignment for default case."""
        task = {
            "title": "Regular Task",
            "description": "Do some regular work",
            "deadline": datetime(2024, 3, 26, 17, 0, 0),  # 6 days away (< 7 days)
            "owner": "john@example.com",
            "confidence": 0.9,
            "source_snippet": "Regular task",
        }

        current_time = datetime(2024, 3, 20, 10, 0, 0)
        result = service._assign_priority(task, current_time)

        assert result["priority"] == "medium"

    def test_resolve_deadline_relative(self, service):
        """Test relative deadline resolution."""
        task = {
            "title": "Task",
            "description": "Description",
            "deadline": "2024-03-21",
            "owner": "john@example.com",
            "confidence": 0.9,
            "source_snippet": "Task",
        }

        current_time = datetime(2024, 3, 20, 10, 0, 0)
        result = service._resolve_deadline(task, current_time)

        # Deadline should be resolved to a datetime
        assert isinstance(result["deadline"], datetime)

    def test_resolve_deadline_absolute(self, service):
        """Test absolute deadline is preserved."""
        task = {
            "title": "Task",
            "description": "Description",
            "deadline": datetime(2024, 3, 25, 14, 0, 0),
            "owner": "john@example.com",
            "confidence": 0.9,
            "source_snippet": "Task",
        }

        current_time = datetime(2024, 3, 20, 10, 0, 0)
        result = service._resolve_deadline(task, current_time)

        # Deadline should remain as datetime
        assert isinstance(result["deadline"], datetime)

    def test_process_tasks_full_flow(self, service):
        """Test full task processing flow."""
        tasks = [
            {
                "title": "Urgent Task",
                "description": "Do this now",
                "deadline": datetime(2024, 3, 21, 17, 0, 0),
                "owner": "john@example.com",
                "confidence": 0.9,
                "source_snippet": "Urgent task",
            },
            {
                "title": "Regular Task",
                "description": "Do this later",
                "deadline": datetime(2024, 3, 26, 17, 0, 0),  # 6 days away (< 7 days)
                "owner": "jane@example.com",
                "confidence": 0.85,
                "source_snippet": "Regular task",
            },
        ]

        current_time = datetime(2024, 3, 20, 10, 0, 0)
        result = service.process_tasks(tasks, current_time)

        assert len(result) == 2
        assert result[0]["priority"] == "high"  # Urgent keyword
        assert result[1]["priority"] == "medium"  # Default (6 days, < 7 days)

    def test_assign_priority_multiple_urgent_keywords(self, service):
        """Test priority elevation with multiple urgent keywords."""
        task = {
            "title": "URGENT: ASAP: Critical Emergency Fix",
            "description": "This is immediately critical and urgent",
            "deadline": datetime(2024, 4, 1, 17, 0, 0),  # More than 24h away
            "owner": "john@example.com",
            "confidence": 0.9,
            "source_snippet": "Multiple urgent keywords here",
        }

        current_time = datetime(2024, 3, 20, 10, 0, 0)
        result = service._assign_priority(task, current_time)

        assert result["priority"] == "high"

    def test_resolve_deadline_ambiguous_format(self, service):
        """Test handling of ambiguous deadline formats."""
        task = {
            "title": "Task",
            "description": "Description",
            "deadline": "03/21/2024",  # MM/DD/YYYY format
            "owner": "john@example.com",
            "confidence": 0.9,
            "source_snippet": "Task",
        }

        current_time = datetime(2024, 3, 20, 10, 0, 0)
        result = service._resolve_deadline(task, current_time)

        # Should resolve to a datetime without crashing
        assert isinstance(result["deadline"], datetime)

    def test_resolve_deadline_far_future(self, service):
        """Test handling of far future dates."""
        task = {
            "title": "Task",
            "description": "Description",
            "deadline": "2030-12-31",
            "owner": "john@example.com",
            "confidence": 0.9,
            "source_snippet": "Task",
        }

        current_time = datetime(2024, 3, 20, 10, 0, 0)
        result = service._resolve_deadline(task, current_time)

        assert isinstance(result["deadline"], datetime)
        assert result["deadline"].year == 2030

    def test_resolve_deadline_far_past(self, service):
        """Test handling of far past dates (should still resolve)."""
        task = {
            "title": "Task",
            "description": "Description",
            "deadline": "2020-01-01",
            "owner": "john@example.com",
            "confidence": 0.9,
            "source_snippet": "Task",
        }

        current_time = datetime(2024, 3, 20, 10, 0, 0)
        result = service._resolve_deadline(task, current_time)

        # Should resolve to a datetime (even if in the past)
        assert isinstance(result["deadline"], datetime)

    def test_assign_priority_low_priority_far_future(self, service):
        """Test low priority assignment for tasks far in the future."""
        task = {
            "title": "Future Task",
            "description": "Do this much later",
            "deadline": datetime(2024, 12, 31, 17, 0, 0),  # More than 7 days away
            "owner": "john@example.com",
            "confidence": 0.9,
            "source_snippet": "Future task",
        }

        current_time = datetime(2024, 3, 20, 10, 0, 0)
        result = service._assign_priority(task, current_time)

        # Should be low priority since it's more than 7 days away
        assert result["priority"] == "low"

    def test_process_tasks_empty_list(self, service):
        """Test processing empty task list."""
        tasks = []

        current_time = datetime(2024, 3, 20, 10, 0, 0)
        result = service.process_tasks(tasks, current_time)

        assert result == []

    def test_process_tasks_with_missing_deadline(self, service):
        """Test processing tasks with missing deadline field."""
        task = {
            "title": "Task",
            "description": "Description",
            "owner": "john@example.com",
            "confidence": 0.9,
            "source_snippet": "Task",
        }

        tasks = [task]
        current_time = datetime(2024, 3, 20, 10, 0, 0)
        
        # Should not crash when deadline is missing
        result = service.process_tasks(tasks, current_time)
        
        assert len(result) == 1
        assert result[0]["priority"] == "medium"  # Default when deadline missing
