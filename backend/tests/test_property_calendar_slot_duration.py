"""Property-based tests for calendar slot duration."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta

from src.services.calendar import CalendarService


def get_service():
    """Get a new CalendarService instance."""
    return CalendarService()


@given(
    event_count=st.integers(min_value=0, max_value=10),
    slot_duration=st.integers(min_value=30, max_value=60),
)
@settings(max_examples=100)
def test_property_8_slot_duration_is_at_least_30_minutes(
    event_count, slot_duration
):
    """
    Property 8: Calendar Slot Duration Invariant

    For any calendar slot found,
    the duration should be at least 30 minutes.
    """
    service = get_service()
    # Create events that would result in a slot of specified duration
    events = []
    for i in range(event_count):
        events.append({
            "start": {"dateTime": f"2024-03-20T{9+i:02d}:00:00Z"},
            "end": {"dateTime": f"2024-03-20T{10+i:02d}:00:00Z"},
        })

    start_time = datetime(2024, 3, 20, 10, 0, 0)
    deadline = datetime(2024, 3, 20, 17, 0, 0)

    slot = service._find_nearest_available_slot(events, start_time, deadline)

    if slot is not None:
        slot_start, slot_end = slot
        duration_minutes = (slot_end - slot_start).total_seconds() / 60
        assert duration_minutes >= 30, f"Slot duration {duration_minutes}min is less than 30min"


@given(
    event_count=st.integers(min_value=0, max_value=10),
    slot_duration=st.integers(min_value=30, max_value=60),
)
@settings(max_examples=100)
def test_property_8_slot_duration_is_at_most_60_minutes(
    event_count, slot_duration
):
    """
    Property 8: Calendar Slot Duration Invariant

    For any calendar slot found,
    the duration should be at most 60 minutes.
    """
    service = get_service()
    events = []
    for i in range(event_count):
        events.append({
            "start": {"dateTime": f"2024-03-20T{9+i:02d}:00:00Z"},
            "end": {"dateTime": f"2024-03-20T{10+i:02d}:00:00Z"},
        })

    start_time = datetime(2024, 3, 20, 10, 0, 0)
    deadline = datetime(2024, 3, 20, 17, 0, 0)

    slot = service._find_nearest_available_slot(events, start_time, deadline)

    if slot is not None:
        slot_start, slot_end = slot
        duration_minutes = (slot_end - slot_start).total_seconds() / 60
        assert duration_minutes <= 60, f"Slot duration {duration_minutes}min exceeds 60min"


@given(
    event_count=st.integers(min_value=0, max_value=10),
)
@settings(max_examples=100)
def test_property_8_slot_duration_is_within_30_to_60_minutes(
    event_count
):
    """
    Property 8: Calendar Slot Duration Invariant

    For any calendar slot found,
    the duration should be between 30 and 60 minutes inclusive.
    """
    service = get_service()
    events = []
    for i in range(event_count):
        events.append({
            "start": {"dateTime": f"2024-03-20T{9+i:02d}:00:00Z"},
            "end": {"dateTime": f"2024-03-20T{10+i:02d}:00:00Z"},
        })

    start_time = datetime(2024, 3, 20, 10, 0, 0)
    deadline = datetime(2024, 3, 20, 17, 0, 0)

    slot = service._find_nearest_available_slot(events, start_time, deadline)

    if slot is not None:
        slot_start, slot_end = slot
        duration_minutes = (slot_end - slot_start).total_seconds() / 60
        assert 30 <= duration_minutes <= 60, f"Slot duration {duration_minutes}min is not in [30, 60]"
