"""
Pydantic models for the AI Execution Agent API.

This module defines all request and response models used by the backend API.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ThreadMessageModel(BaseModel):
    """Model for a message in an email thread."""
    sender: str
    timestamp: str
    body: str


class ForwardedMessageModel(BaseModel):
    """Model for a forwarded message in an email."""
    original_sender: str
    original_timestamp: str
    body: str


class EmailContentModel(BaseModel):
    """Model for extracted email content."""
    subject: str
    body: str
    sender: str
    timestamp: str
    thread_messages: List[ThreadMessageModel] = Field(default_factory=list)
    forwarded_messages: List[ForwardedMessageModel] = Field(default_factory=list)


class TaskModel(BaseModel):
    """Model for an extracted task."""
    id: str
    title: str
    description: str
    deadline: datetime
    owner: Optional[str] = "Unknown"
    confidence: float = Field(ge=0.0, le=1.0)
    priority: str
    state: str
    calendar_block_id: Optional[str] = None
    source_snippet: str

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is between 0.0 and 1.0."""
        if not (0.0 <= v <= 1.0):
            raise ValueError('confidence must be between 0.0 and 1.0')
        return v


class FeedbackStatsModel(BaseModel):
    """Model for feedback statistics."""
    tasks_extracted: int
    calendar_blocks_created: int
    scheduling_conflicts: int
    manual_review_items: int


class LogEntryModel(BaseModel):
    """Model for execution log entries."""
    timestamp: datetime
    message: str
    level: str = Field(default="INFO")


class ErrorDetailModel(BaseModel):
    """Model for error details."""
    code: str
    message: str
    context: Optional[dict] = Field(default=None)


class RunAgentRequestModel(BaseModel):
    """Model for the /run-agent request."""
    email_content: EmailContentModel
    user_timezone: str
    calendar_id: str


class RunAgentResponseModel(BaseModel):
    """Model for the /run-agent response."""
    tasks: List[TaskModel]
    stats: FeedbackStatsModel
    logs: List[LogEntryModel]
    errors: List[ErrorDetailModel] = Field(default_factory=list)


class MeetingPrepDocument(BaseModel):
    """Model for meeting preparation document."""
    meeting_title: str
    meeting_time: datetime
    context_summary: str
    talking_points: List[str]
    questions: List[str]
    risks: List[str]
