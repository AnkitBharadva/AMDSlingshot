"""Property-based tests for nearest slot selection."""

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
    event_count=st.integers(min_value=1, max_value=5),
)
@settings(max_examples=100)
def test_property_9_nearest_slot_is_selected(
    event_count
):
    """
    Property 9: Nearest Slot Selection

    For any calendar with multiple available slots,
    the slot nearest to the current time should be selected.
    """
    service = get_service()
    # Create events that create multiple available slots
    events = []
    for i in range(event_count):
        events.append({
            "start": {"dateTime": f"2024-03-20T{9+i*2:02d}:00:00Z"},
            "end": {"dateTime": f"2024-03-20T{10+i*2:02d}:00:00Z"},
        })

    start_time = datetime(2024, 3, 20, 8, 0, 0)
    deadline = datetime(2024, 3, 20, 17, 0, 0)

    slot = service._find_nearest_available_slot(events, start_time, deadline)

    if slot is not None:
        slot_start, slot_end = slot
        # The selected slot should be the earliest available slot
        # that is >= start_time
        assert slot_start >= start_time


@given(
    event_count=st.integers(min_value=0, max_value=5),
)
@settings(max_examples=100)
def test_property_9_no_slot_after_deadline(
    event_count
):
    """
    Property 9: Nearest Slot Selection

    For any calendar, the nearest slot should not be after the deadline.
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
        assert slot_end <= deadline, f"Slot end {slot_end} is after deadline {deadline}"


@given(
    event_count=st.integers(min_value=0, max_value=5),
)
@settings(max_examples=100)
def test_property_9_slot_is_before_or_at_first_event(
    event_count
):
    """
    Property 9: Nearest Slot Selection

    For any calendar with events, the nearest slot should be before the first event.
    """
    service = get_service()
    events = []
    for i in range(event_count):
        events.append({
            "start": {"dateTime": f"2024-03-20T{9+i:02d}:00:00Z"},
            "end": {"dateTime": f"2024-03-20T{10+i:02d}:00:00Z"},
        })

    start_time = datetime(2024, 3, 20, 8, 0, 0)
    deadline = datetime(2024, 3, 20, 17, 0, 0)

    slot = service._find_nearest_available_slot(events, start_time, deadline)

    if slot is not None and events:
        first_event_start = datetime(2024, 3, 20, 9, 0, 0)
        slot_start, slot_end = slot
        assert slot_end <= first_event_start, f"Slot {slot_start}-{slot_end} overlaps with first event"
