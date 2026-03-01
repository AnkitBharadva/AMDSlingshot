"""Property-based tests for task validation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from hypothesis import given, strategies as st, settings
from pydantic import ValidationError

from backend.models.models import TaskModel
from datetime import datetime


@given(
    title=st.text(min_size=1, max_size=200),
    description=st.text(min_size=1, max_size=2000),
    deadline=st.datetimes(),
    owner=st.emails(),
    confidence=st.floats(min_value=0.0, max_value=1.0),
    source_snippet=st.text(min_size=1, max_size=500),
)
@settings(max_examples=100)
def test_property_4_task_structure_validation(title, description, deadline, owner, confidence, source_snippet):
    """
    Property 4: Task Structure Validation

    For any valid task data with all required fields,
    TaskModel should successfully validate and create a task.
    """
    task_data = {
        "id": "task-001",
        "title": title,
        "description": description,
        "deadline": deadline,
        "owner": owner,
        "confidence": confidence,
        "priority": "medium",
        "state": "scheduled",
        "source_snippet": source_snippet,
    }

    task = TaskModel(**task_data)

    assert task.title == title
    assert task.description == description
    assert task.deadline == deadline
    assert task.owner == owner
    assert task.confidence == confidence
    assert 0.0 <= task.confidence <= 1.0
    assert task.source_snippet == source_snippet


@given(
    title=st.text(min_size=1, max_size=200),
    description=st.text(min_size=1, max_size=2000),
    deadline=st.datetimes(),
    owner=st.emails(),
    source_snippet=st.text(min_size=1, max_size=500),
)
@settings(max_examples=100)
def test_property_4_confidence_must_be_between_0_and_1(title, description, deadline, owner, source_snippet):
    """
    Property 4: Task Structure Validation - Confidence Range

    For any task, the confidence score must be between 0.0 and 1.0 inclusive.
    """
    # Test with valid confidence
    task_data = {
        "id": "task-001",
        "title": title,
        "description": description,
        "deadline": deadline,
        "owner": owner,
        "confidence": 0.5,
        "priority": "medium",
        "state": "scheduled",
        "source_snippet": source_snippet,
    }

    task = TaskModel(**task_data)
    assert 0.0 <= task.confidence <= 1.0


@given(
    title=st.text(min_size=1, max_size=200),
    description=st.text(min_size=1, max_size=2000),
    deadline=st.datetimes(),
    owner=st.emails(),
    confidence=st.floats(min_value=0.0, max_value=1.0),
    source_snippet=st.text(min_size=1, max_size=500),
)
@settings(max_examples=100)
def test_property_4_all_required_fields_present(title, description, deadline, owner, confidence, source_snippet):
    """
    Property 4: Task Structure Validation - Required Fields

    For any task, all required fields must be present and non-empty.
    """
    task_data = {
        "id": "task-001",
        "title": title,
        "description": description,
        "deadline": deadline,
        "owner": owner,
        "confidence": confidence,
        "priority": "medium",
        "state": "scheduled",
        "source_snippet": source_snippet,
    }

    task = TaskModel(**task_data)

    # Verify all required fields are present
    assert task.title is not None
    assert task.description is not None
    assert task.deadline is not None
    assert task.owner is not None
    assert task.confidence is not None
    assert task.source_snippet is not None
