"""Tests for calendar service."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from backend.src.services.calendar import CalendarService


class TestCalendarService:
    """Tests for CalendarService."""

    @pytest.fixture
    def service(self):
        """Calendar service instance."""
        return CalendarService()

    def test_find_slot_and_create_block_no_service(self, service):
        """Test slot finding when calendar service is not available."""
        task = {
            "title": "Test Task",
            "description": "Test Description",
            "deadline": datetime(2024, 3, 25, 17, 0, 0),
            "owner": "john@example.com",
            "confidence": 0.9,
            "source_snippet": "Test",
        }

        block_id, error = service.find_slot_and_create_block(task, "primary")

        assert block_id is None
        assert error == "calendar_api_not_available"

    def test_find_nearest_available_slot_empty_calendar(self, service):
        """Test slot finding with empty calendar."""
        events = []
        start_time = datetime(2024, 3, 20, 10, 0, 0)
        deadline = datetime(2024, 3, 20, 17, 0, 0)

        slot = service._find_nearest_available_slot(events, start_time, deadline)

        # With empty calendar, slot should be found
        assert slot is not None
        slot_start, slot_end = slot
        assert (slot_end - slot_start).total_seconds() / 60 >= 30

    def test_find_nearest_available_slot_with_events(self, service):
        """Test slot finding with existing events."""
        events = [
            {
                "start": {"dateTime": "2024-03-20T09:00:00Z"},
                "end": {"dateTime": "2024-03-20T10:00:00Z"},
            },
            {
                "start": {"dateTime": "2024-03-20T11:00:00Z"},
                "end": {"dateTime": "2024-03-20T12:00:00Z"},
            },
        ]
        start_time = datetime(2024, 3, 20, 10, 0, 0)
        deadline = datetime(2024, 3, 20, 17, 0, 0)

        slot = service._find_nearest_available_slot(events, start_time, deadline)

        # Should find slot after first event (10:00-11:00)
        assert slot is not None

    def test_find_nearest_available_slot_no_available_slot(self, service):
        """Test slot finding when no slot is available."""
        # Calendar fully booked with events covering all time
        events = [
            {
                "start": {"dateTime": "2024-03-20T09:00:00Z"},
                "end": {"dateTime": "2024-03-20T10:00:00Z"},
            },
            {
                "start": {"dateTime": "2024-03-20T10:00:00Z"},
                "end": {"dateTime": "2024-03-20T11:00:00Z"},
            },
            {
                "start": {"dateTime": "2024-03-20T11:00:00Z"},
                "end": {"dateTime": "2024-03-20T12:00:00Z"},
            },
        ]
        start_time = datetime(2024, 3, 20, 10, 0, 0)
        deadline = datetime(2024, 3, 20, 12, 30, 0)

        slot = service._find_nearest_available_slot(events, start_time, deadline)

        # Slot should be found after last event (12:00-12:30)
        assert slot is not None
        slot_start, slot_end = slot
        assert slot_end <= deadline

    def test_find_nearest_available_slot_before_deadline(self, service):
        """Test that slot is found before deadline."""
        events = []
        start_time = datetime(2024, 3, 20, 10, 0, 0)
        deadline = datetime(2024, 3, 20, 11, 0, 0)

        slot = service._find_nearest_available_slot(events, start_time, deadline)

        # With empty calendar, slot should be found
        assert slot is not None
        slot_start, slot_end = slot
        assert slot_end <= deadline

    def test_parse_event_time_datetime(self, service):
        """Test parsing event time with datetime."""
        time_dict = {"dateTime": "2024-03-20T10:00:00Z"}

        result = service._parse_event_time(time_dict)

        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 3
        assert result.day == 20

    def test_parse_event_time_date(self, service):
        """Test parsing event time with date only."""
        time_dict = {"date": "2024-03-20"}

        result = service._parse_event_time(time_dict)

        assert isinstance(result, datetime)
