"""Pytest configuration for backend tests."""

import pytest
from datetime import datetime


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter before each test to avoid rate limit issues."""
    from backend.src.security import RateLimiter
    from backend.src.main import rate_limiter
    # Reset the rate limiter used in main.py
    rate_limiter.requests.clear()


@pytest.fixture
def sample_email_content():
    """Sample email content for testing."""
    from models.models import EmailContentModel, ThreadMessageModel

    return EmailContentModel(
        subject="Project Update Meeting",
        body="Hi team, let's schedule a meeting to discuss the project timeline.",
        sender="john@example.com",
        timestamp="2024-03-15T10:00:00Z",
        thread_messages=[
            ThreadMessageModel(
                sender="jane@example.com",
                timestamp="2024-03-15T09:30:00Z",
                body="Can we discuss the timeline?"
            )
        ],
        forwarded_messages=[]
    )


@pytest.fixture
def sample_task():
    """Sample task for testing."""
    return {
        "id": "task-001",
        "title": "Project Meeting",
        "description": "Discuss project timeline",
        "deadline": datetime(2024, 3, 20, 14, 0, 0),
        "owner": "john@example.com",
        "confidence": 0.9,
        "priority": "high",
        "state": "scheduled",
        "source_snippet": "Let's schedule a meeting to discuss the project timeline.",
    }


@pytest.fixture
def sample_tasks():
    """Sample list of tasks for testing."""
    return [
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
            "title": "Review Documentation",
            "description": "Review API documentation",
            "deadline": datetime(2024, 3, 25, 17, 0, 0),
            "owner": "jane@example.com",
            "confidence": 0.85,
            "priority": "medium",
            "state": "scheduled",
            "source_snippet": "Please review the documentation.",
        },
    ]
