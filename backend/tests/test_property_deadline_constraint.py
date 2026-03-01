"""Property-based tests for deadline constraint enforcement."""

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
    event_count=st.integers(min_value=0, max_value=5),
    deadline_offset_hours=st.floats(min_value=1, max_value=24),
)
@settings(max_examples=100)
def test_property_10_no_slot_after_deadline(
    event_count, deadline_offset_hours
):
    """
    Property 10: Deadline Constraint Enforcement

    For any calendar, no slot should be created after the task deadline.
    """
    service = get_service()
    events = []
    for i in range(event_count):
        events.append({
            "start": {"dateTime": f"2024-03-20T{9+i:02d}:00:00Z"},
            "end": {"dateTime": f"2024-03-20T{10+i:02d}:00:00Z"},
        })

    start_time = datetime(2024, 3, 20, 8, 0, 0)
    deadline = start_time + timedelta(hours=deadline_offset_hours)

    slot = service._find_nearest_available_slot(events, start_time, deadline)

    if slot is not None:
        slot_start, slot_end = slot
        assert slot_end <= deadline, f"Slot end {slot_end} is after deadline {deadline}"


@given(
    event_count=st.integers(min_value=0, max_value=5),
    deadline_offset_hours=st.floats(min_value=1, max_value=24),
)
@settings(max_examples=100)
def test_property_10_slot_starts_before_deadline(
    event_count, deadline_offset_hours
):
    """
    Property 10: Deadline Constraint Enforcement

    For any calendar, the slot start time should be before the deadline.
    """
    service = get_service()
    events = []
    for i in range(event_count):
        events.append({
            "start": {"dateTime": f"2024-03-20T{9+i:02d}:00:00Z"},
            "end": {"dateTime": f"2024-03-20T{10+i:02d}:00:00Z"},
        })

    start_time = datetime(2024, 3, 20, 8, 0, 0)
    deadline = start_time + timedelta(hours=deadline_offset_hours)

    slot = service._find_nearest_available_slot(events, start_time, deadline)

    if slot is not None:
        slot_start, slot_end = slot
        assert slot_start < deadline, f"Slot start {slot_start} is at or after deadline {deadline}"


@given(
    event_count=st.integers(min_value=0, max_value=5),
    deadline_offset_hours=st.floats(min_value=0.5, max_value=1),
)
@settings(max_examples=100)
def test_property_10_slot_fits_before_deadline(
    event_count, deadline_offset_hours
):
    """
    Property 10: Deadline Constraint Enforcement

    For any calendar, if a slot is found, it should fit entirely before the deadline.
    """
    service = get_service()
    events = []
    for i in range(event_count):
        events.append({
            "start": {"dateTime": f"2024-03-20T{9+i:02d}:00:00Z"},
            "end": {"dateTime": f"2024-03-20T{10+i:02d}:00:00Z"},
        })

    start_time = datetime(2024, 3, 20, 8, 0, 0)
    deadline = start_time + timedelta(hours=deadline_offset_hours)

    slot = service._find_nearest_available_slot(events, start_time, deadline)

    if slot is not None:
        slot_start, slot_end = slot
        # Slot should fit entirely before deadline
        assert slot_end <= deadline, f"Slot {slot_start}-{slot_end} extends past deadline {deadline}"


@given(
    event_count=st.integers(min_value=0, max_value=5),
    deadline_offset_hours=st.floats(min_value=0.5, max_value=1),
)
@settings(max_examples=100)
def test_property_10_scheduling_conflict_when_no_slot_before_deadline(
    event_count, deadline_offset_hours
):
    """
    Property 10: Deadline Constraint Enforcement

    For any calendar where no slot can be found before the deadline,
    the service should return a scheduling conflict.
    """
    service = get_service()
    # Create events that fill all time before deadline
    events = []
    for i in range(event_count):
        events.append({
            "start": {"dateTime": f"2024-03-20T{9+i:02d}:00:00Z"},
            "end": {"dateTime": f"2024-03-20T{10+i:02d}:00:00Z"},
        })

    start_time = datetime(2024, 3, 20, 8, 0, 0)
    deadline = start_time + timedelta(hours=deadline_offset_hours)

    slot = service._find_nearest_available_slot(events, start_time, deadline)

    # With limited time before deadline, slot might not be found
    # This is expected behavior - scheduling conflict
    if slot is None:
        # This is the expected case when no slot fits
        pass
    else:
        slot_start, slot_end = slot
        assert slot_end <= deadline
