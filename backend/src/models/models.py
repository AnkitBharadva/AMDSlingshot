"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskState(str, Enum):
    SCHEDULED = "scheduled"
    MANUAL_REVIEW = "manual_review"
    SCHEDULING_CONFLICT = "scheduling_conflict"
    DISCARDED = "discarded"


class EmailContentModel(BaseModel):
    subject: str
    body: str
    sender: str
    timestamp: str
    thread_messages: List["ThreadMessageModel"] = []
    forwarded_messages: List["ForwardedMessageModel"] = []


class ThreadMessageModel(BaseModel):
    sender: str
    timestamp: str
    body: str


class ForwardedMessageModel(BaseModel):
    original_sender: str
    original_timestamp: str
    body: str


class RunAgentRequestModel(BaseModel):
    email_content: EmailContentModel
    user_timezone: str
    calendar_id: str


class TaskModel(BaseModel):
    id: str
    title: str
    description: str
    deadline: datetime
    owner: str
    confidence: float = Field(ge=0.0, le=1.0)
    priority: str
    state: str
    calendar_block_id: Optional[str] = None
    source_snippet: str


class RunAgentResponseModel(BaseModel):
    tasks: List[TaskModel]
    stats: "FeedbackStatsModel"
    logs: List["LogEntryModel"]
    errors: List["ErrorDetailModel"]


class FeedbackStatsModel(BaseModel):
    tasks_extracted: int
    calendar_blocks_created: int
    scheduling_conflicts: int
    manual_review_items: int


class LogEntryModel(BaseModel):
    timestamp: datetime
    message: str
    level: str = "info"


class ErrorDetailModel(BaseModel):
    code: str
    message: str
    context: Optional[dict] = None


class MeetingPrepDocument(BaseModel):
    meeting_title: str
    meeting_time: datetime
    context_summary: str
    talking_points: List[str]
    questions: List[str]
    risks: List[str]
