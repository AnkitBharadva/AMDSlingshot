"""
Property-based tests for Pydantic models.

Validates that task structure and validation rules are correctly enforced.
"""

import pytest
from hypothesis import given, strategies as st
from datetime import datetime
from backend.models.models import TaskModel


# Feature: ai-execution-agent, Property 4: Task Structure Validation
@given(
    id=st.text(min_size=1, max_size=100),
    title=st.text(min_size=1, max_size=200),
    description=st.text(min_size=1, max_size=2000),
    deadline=st.datetimes(),
    owner=st.text(min_size=1, max_size=100),
    confidence=st.floats(min_value=0.0, max_value=1.0),
    priority=st.sampled_from(["low", "medium", "high"]),
    state=st.sampled_from(["scheduled", "manual_review", "scheduling_conflict", "discarded"]),
    source_snippet=st.text(min_size=1, max_size=500)
)
def test_task_model_valid_structure(id, title, description, deadline, owner, confidence, priority, state, source_snippet):
    """
    Property 4: Task Structure Validation
    
    For any valid task data with all required fields, the TaskModel should
    successfully validate and create a valid task instance.
    
    Validates: Requirements 2.3, 2.4, 2.5, 2.6, 2.7, 2.8
    """
    task = TaskModel(
        id=id,
        title=title,
        description=description,
        deadline=deadline,
        owner=owner,
        confidence=confidence,
        priority=priority,
        state=state,
        source_snippet=source_snippet
    )
    
    assert task.id == id
    assert task.title == title
    assert task.description == description
    assert task.deadline == deadline
    assert task.owner == owner
    assert task.confidence == confidence
    assert task.priority == priority
    assert task.state == state
    assert task.source_snippet == source_snippet


def test_task_model_confidence_boundary_low():
    """
    Test that confidence value of 0.0 is valid (lower boundary).
    """
    task = TaskModel(
        id="task-1",
        title="Test Task",
        description="Test Description",
        deadline=datetime.now(),
        owner="test@example.com",
        confidence=0.0,
        priority="low",
        state="scheduled",
        source_snippet="Test snippet"
    )
    assert task.confidence == 0.0


def test_task_model_confidence_boundary_high():
    """
    Test that confidence value of 1.0 is valid (upper boundary).
    """
    task = TaskModel(
        id="task-1",
        title="Test Task",
        description="Test Description",
        deadline=datetime.now(),
        owner="test@example.com",
        confidence=1.0,
        priority="high",
        state="scheduled",
        source_snippet="Test snippet"
    )
    assert task.confidence == 1.0


def test_task_model_confidence_invalid_below_zero():
    """
    Test that confidence value below 0.0 raises validation error.
    """
    with pytest.raises(Exception):  # Pydantic raises ValidationError
        TaskModel(
            id="task-1",
            title="Test Task",
            description="Test Description",
            deadline=datetime.now(),
            owner="test@example.com",
            confidence=-0.1,
            priority="low",
            state="scheduled",
            source_snippet="Test snippet"
        )


def test_task_model_confidence_invalid_above_one():
    """
    Test that confidence value above 1.0 raises validation error.
    """
    with pytest.raises(Exception):  # Pydantic raises ValidationError
        TaskModel(
            id="task-1",
            title="Test Task",
            description="Test Description",
            deadline=datetime.now(),
            owner="test@example.com",
            confidence=1.1,
            priority="high",
            state="scheduled",
            source_snippet="Test snippet"
        )


@given(
    confidence=st.floats(allow_nan=False, allow_infinity=False).filter(
        lambda x: x < 0.0 or x > 1.0
    )
)
def test_task_model_confidence_invalid_out_of_range(confidence):
    """
    Property 4: Task Structure Validation
    
    For any confidence value outside [0.0, 1.0], TaskModel should raise
    a validation error.
    
    Validates: Requirements 2.3, 2.4, 2.5, 2.6, 2.7, 2.8
    """
    with pytest.raises(Exception):
        TaskModel(
            id="task-1",
            title="Test Task",
            description="Test Description",
            deadline=datetime.now(),
            owner="test@example.com",
            confidence=confidence,
            priority="low",
            state="scheduled",
            source_snippet="Test snippet"
        )
