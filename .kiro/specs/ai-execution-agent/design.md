# Design Document: AI Execution Agent

## Overview

The AI Execution Agent is a Chrome Extension with FastAPI backend that extracts actionable tasks from Gmail emails, schedules them on Google Calendar, and generates meeting preparation documents. The system follows a user-initiated, stateless architecture with deterministic behavior.

The architecture consists of:
- **Frontend**: Chrome Extension (Manifest V3) with TypeScript, vanilla DOM manipulation
- **Backend**: Python FastAPI server with Pydantic validation, LLM integration, Google Calendar API
- **Communication**: RESTful API over HTTPS
- **Storage**: In-memory or SQLite for temporary data only

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Gmail Web UI                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Chrome Extension (Content Script)          │    │
│  │  - DOM Extraction                                   │    │
│  │  - "Run Agent" Button Injection                    │    │
│  │  - Task Board UI Rendering                         │    │
│  └────────────────┬───────────────────────────────────┘    │
└───────────────────┼────────────────────────────────────────┘
                    │ HTTPS POST /run-agent
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Layer (Pydantic validation, CORS)              │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               ▼                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Task Extraction Service                             │  │
│  │  - LLM Integration (OpenAI/Gemini)                   │  │
│  │  - JSON Parsing & Validation                         │  │
│  │  - Retry Logic                                       │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               ▼                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Post-Processing Service                             │  │
│  │  - Priority Assignment (Rule-based)                  │  │
│  │  - Deadline Resolution (python-dateutil)             │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               ▼                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Calendar Service                                    │  │
│  │  - Google Calendar API Integration                   │  │
│  │  - Slot Finding Algorithm                            │  │
│  │  - Block Creation                                    │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               ▼                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Meeting Prep Service                                │  │
│  │  - Meeting Detection                                 │  │
│  │  - Document Generation (LLM)                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. User clicks "Run Agent" button in Gmail
2. Extension extracts email content via DOM
3. Extension sends POST request to `/run-agent` with email data
4. Backend validates request with Pydantic
5. Task Extraction Service calls LLM with structured prompt
6. Post-Processing Service applies priority rules and resolves deadlines
7. Calendar Service queries Google Calendar and finds available slots
8. Calendar Service creates calendar blocks (if slots available)
9. Meeting Prep Service detects meetings and generates prep documents
10. Backend returns structured response with tasks, stats, and any errors
11. Extension renders task board, feedback panel, and logs

## Components and Interfaces

### Chrome Extension Components

#### Content Script (`content.ts`)

Responsible for DOM manipulation and email extraction.

```typescript
interface EmailContent {
  subject: string;
  body: string;
  sender: string;
  timestamp: string;
  threadMessages: ThreadMessage[];
  forwardedMessages: ForwardedMessage[];
}

interface ThreadMessage {
  sender: string;
  timestamp: string;
  body: string;
}

interface ForwardedMessage {
  originalSender: string;
  originalTimestamp: string;
  body: string;
}

class GmailDOMExtractor {
  injectRunAgentButton(): void
  extractEmailContent(): EmailContent
  extractThreadMessages(): ThreadMessage[]
  extractForwardedMessages(): ForwardedMessage[]
}
```

#### UI Renderer (`ui.ts`)

Renders task board, feedback panel, and logs.

```typescript
interface TaskDisplayData {
  id: string;
  title: string;
  description: string;
  deadline: string;
  owner: string;
  confidence: number;
  priority: Priority;
  state: TaskState;
  calendarBlockId?: string;
}

enum Priority {
  Low = "low",
  Medium = "medium",
  High = "high"
}

enum TaskState {
  Scheduled = "scheduled",
  ManualReview = "manual_review",
  SchedulingConflict = "scheduling_conflict",
  Discarded = "discarded"
}

interface FeedbackStats {
  tasksExtracted: number;
  calendarBlocksCreated: number;
  schedulingConflicts: number;
  manualReviewItems: number;
}

class TaskBoardRenderer {
  renderTaskBoard(tasks: TaskDisplayData[]): void
  renderFeedbackPanel(stats: FeedbackStats): void
  renderExecutionLog(logs: LogEntry[]): void
  groupTasksByTimeline(tasks: TaskDisplayData[]): TimelineGroups
}

interface TimelineGroups {
  today: TaskDisplayData[];
  tomorrow: TaskDisplayData[];
  upcoming: TaskDisplayData[];
}
```

#### API Client (`api.ts`)

Handles communication with backend.

```typescript
interface RunAgentRequest {
  emailContent: EmailContent;
  userTimezone: string;
  calendarId: string;
}

interface RunAgentResponse {
  tasks: TaskDisplayData[];
  stats: FeedbackStats;
  logs: LogEntry[];
  errors: ErrorDetail[];
}

interface ErrorDetail {
  code: string;
  message: string;
  context?: Record<string, any>;
}

class BackendAPIClient {
  async runAgent(request: RunAgentRequest): Promise<RunAgentResponse>
}
```

#### Task Actions (`actions.ts`)

Handles user interactions with tasks.

```typescript
class TaskActionHandler {
  adjustDeadline(taskId: string, newDeadline: Date): void
  discardTask(taskId: string): void
  exportTasksToCSV(tasks: TaskDisplayData[]): void
  exportMeetingPrepToPDF(prepDocument: MeetingPrepDocument): void
}
```

### Backend Components

#### API Layer (`main.py`, `models.py`)

FastAPI application with Pydantic models.

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

class EmailContentModel(BaseModel):
    subject: str
    body: str
    sender: str
    timestamp: str
    thread_messages: List[ThreadMessageModel] = []
    forwarded_messages: List[ForwardedMessageModel] = []

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
    stats: FeedbackStatsModel
    logs: List[LogEntryModel]
    errors: List[ErrorDetailModel]

@app.post("/run-agent", response_model=RunAgentResponseModel)
async def run_agent(request: RunAgentRequestModel):
    # Implementation in orchestration layer
    pass
```

#### Task Extraction Service (`services/extraction.py`)

LLM integration for task extraction.

```python
from typing import List, Dict, Any
import json

class TaskExtractionService:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.max_retries = 1
    
    def extract_tasks(self, email_content: EmailContentModel) -> List[Dict[str, Any]]:
        """
        Extract tasks from email content using LLM.
        Returns list of task dictionaries with required fields.
        Retries once on JSON parsing failure.
        """
        prompt = self._build_extraction_prompt(email_content)
        
        for attempt in range(self.max_retries + 1):
            response = self.llm_client.complete(prompt)
            try:
                tasks = json.loads(response)
                validated_tasks = self._validate_task_structure(tasks)
                return validated_tasks
            except json.JSONDecodeError:
                if attempt == self.max_retries:
                    raise ExtractionError("Failed to parse LLM response as JSON")
        
        return []
    
    def _build_extraction_prompt(self, email_content: EmailContentModel) -> str:
        """
        Build structured prompt for LLM task extraction.
        Includes multi-language support configuration.
        """
        pass
    
    def _validate_task_structure(self, tasks: List[Dict]) -> List[Dict]:
        """
        Validate that each task has required fields:
        - title, description, deadline, owner, confidence, source_snippet
        """
        pass

class LLMClient:
    """Abstract interface for LLM providers (OpenAI, Gemini)"""
    def complete(self, prompt: str) -> str:
        pass
```

#### Post-Processing Service (`services/post_processing.py`)

Priority assignment and deadline resolution.

```python
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from typing import Dict, Any

class PostProcessingService:
    URGENT_KEYWORDS = ["urgent", "asap", "immediately", "critical", "emergency"]
    HIGH_PRIORITY_THRESHOLD_HOURS = 24
    
    def process_tasks(self, tasks: List[Dict[str, Any]], current_time: datetime) -> List[Dict[str, Any]]:
        """
        Apply rule-based post-processing to extracted tasks.
        """
        processed = []
        for task in tasks:
            task = self._assign_priority(task, current_time)
            task = self._resolve_deadline(task, current_time)
            processed.append(task)
        return processed
    
    def _assign_priority(self, task: Dict[str, Any], current_time: datetime) -> Dict[str, Any]:
        """
        Rule-based priority assignment:
        - High: deadline < 24 hours OR contains urgent keyword
        - Medium: default
        - Low: explicitly marked or far future
        """
        deadline = task.get("deadline")
        if isinstance(deadline, str):
            deadline = date_parser.parse(deadline)
        
        hours_until_deadline = (deadline - current_time).total_seconds() / 3600
        
        # Check urgent keywords
        text = f"{task.get('title', '')} {task.get('description', '')}".lower()
        has_urgent_keyword = any(keyword in text for keyword in self.URGENT_KEYWORDS)
        
        if hours_until_deadline < self.HIGH_PRIORITY_THRESHOLD_HOURS or has_urgent_keyword:
            task["priority"] = "high"
        else:
            task["priority"] = "medium"
        
        return task
    
    def _resolve_deadline(self, task: Dict[str, Any], current_time: datetime) -> Dict[str, Any]:
        """
        Resolve relative deadline references to absolute dates.
        Uses python-dateutil for parsing.
        """
        deadline_str = task.get("deadline")
        if isinstance(deadline_str, str):
            # Handle relative references like "tomorrow", "next week", "in 3 days"
            task["deadline"] = date_parser.parse(deadline_str, default=current_time)
        return task
```

#### Calendar Service (`services/calendar.py`)

Google Calendar integration and slot finding.

```python
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class CalendarService:
    MIN_BLOCK_DURATION_MINUTES = 30
    MAX_BLOCK_DURATION_MINUTES = 60
    DEFAULT_BLOCK_DURATION_MINUTES = 45
    
    def __init__(self, credentials: Credentials):
        self.service = build('calendar', 'v3', credentials=credentials)
    
    def find_slot_and_create_block(
        self, 
        task: Dict[str, Any], 
        calendar_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Find available slot and create calendar block.
        Returns (calendar_block_id, error_message).
        If no slot found before deadline, returns (None, "scheduling_conflict").
        """
        deadline = task["deadline"]
        current_time = datetime.now()
        
        # Query existing events
        events = self._get_events(calendar_id, current_time, deadline)
        
        # Find available slot
        slot = self._find_nearest_available_slot(events, current_time, deadline)
        
        if slot is None:
            return None, "scheduling_conflict"
        
        # Create calendar block
        block_id = self._create_calendar_block(calendar_id, task, slot)
        return block_id, None
    
    def _get_events(
        self, 
        calendar_id: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[Dict]:
        """Query Google Calendar API for events in time range."""
        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=start_time.isoformat() + 'Z',
            timeMax=end_time.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])
    
    def _find_nearest_available_slot(
        self, 
        events: List[Dict], 
        start_time: datetime, 
        deadline: datetime
    ) -> Optional[Tuple[datetime, datetime]]:
        """
        Find nearest available slot before deadline.
        Slot must be 30-60 minutes.
        Returns (slot_start, slot_end) or None.
        """
        # Sort events by start time
        sorted_events = sorted(events, key=lambda e: e['start'].get('dateTime', e['start'].get('date')))
        
        # Check gap before first event
        if sorted_events:
            first_event_start = self._parse_event_time(sorted_events[0]['start'])
            gap_duration = (first_event_start - start_time).total_seconds() / 60
            if gap_duration >= self.MIN_BLOCK_DURATION_MINUTES:
                slot_end = min(
                    start_time + timedelta(minutes=self.DEFAULT_BLOCK_DURATION_MINUTES),
                    first_event_start,
                    deadline
                )
                if (slot_end - start_time).total_seconds() / 60 >= self.MIN_BLOCK_DURATION_MINUTES:
                    return (start_time, slot_end)
        
        # Check gaps between events
        for i in range(len(sorted_events) - 1):
            current_event_end = self._parse_event_time(sorted_events[i]['end'])
            next_event_start = self._parse_event_time(sorted_events[i + 1]['start'])
            
            gap_duration = (next_event_start - current_event_end).total_seconds() / 60
            
            if gap_duration >= self.MIN_BLOCK_DURATION_MINUTES:
                slot_start = current_event_end
                slot_end = min(
                    slot_start + timedelta(minutes=self.DEFAULT_BLOCK_DURATION_MINUTES),
                    next_event_start,
                    deadline
                )
                if (slot_end - slot_start).total_seconds() / 60 >= self.MIN_BLOCK_DURATION_MINUTES:
                    return (slot_start, slot_end)
        
        # Check gap after last event
        if sorted_events:
            last_event_end = self._parse_event_time(sorted_events[-1]['end'])
            if last_event_end < deadline:
                gap_duration = (deadline - last_event_end).total_seconds() / 60
                if gap_duration >= self.MIN_BLOCK_DURATION_MINUTES:
                    slot_end = min(
                        last_event_end + timedelta(minutes=self.DEFAULT_BLOCK_DURATION_MINUTES),
                        deadline
                    )
                    return (last_event_end, slot_end)
        
        # No slot found before deadline
        return None
    
    def _create_calendar_block(
        self, 
        calendar_id: str, 
        task: Dict[str, Any], 
        slot: Tuple[datetime, datetime]
    ) -> str:
        """Create calendar event and return event ID."""
        event = {
            'summary': task['title'],
            'description': f"{task['description']}\n\nSource: {task['source_snippet']}",
            'start': {
                'dateTime': slot[0].isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': slot[1].isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        created_event = self.service.events().insert(
            calendarId=calendar_id, 
            body=event
        ).execute()
        
        return created_event['id']
    
    def _parse_event_time(self, time_dict: Dict) -> datetime:
        """Parse event time from Google Calendar API response."""
        time_str = time_dict.get('dateTime') or time_dict.get('date')
        return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
```

#### Meeting Prep Service (`services/meeting_prep.py`)

Meeting detection and prep document generation.

```python
from typing import Dict, Any, Optional

class MeetingPrepService:
    MEETING_KEYWORDS = [
        "meeting", "call", "discussion", "sync", "standup", 
        "review", "demo", "presentation", "interview"
    ]
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def detect_and_generate_prep(
        self, 
        task: Dict[str, Any], 
        email_content: EmailContentModel
    ) -> Optional[MeetingPrepDocument]:
        """
        Detect if task is a meeting and generate prep document.
        Returns MeetingPrepDocument or None.
        """
        if not self._is_meeting(task):
            return None
        
        prep_doc = self._generate_prep_document(task, email_content)
        return prep_doc
    
    def _is_meeting(self, task: Dict[str, Any]) -> bool:
        """Detect meeting based on keywords in title/description."""
        text = f"{task.get('title', '')} {task.get('description', '')}".lower()
        return any(keyword in text for keyword in self.MEETING_KEYWORDS)
    
    def _generate_prep_document(
        self, 
        task: Dict[str, Any], 
        email_content: EmailContentModel
    ) -> MeetingPrepDocument:
        """Generate meeting prep document using LLM."""
        prompt = self._build_prep_prompt(task, email_content)
        response = self.llm_client.complete(prompt)
        
        # Parse LLM response into structured document
        prep_doc = self._parse_prep_response(response, task)
        return prep_doc
    
    def _build_prep_prompt(
        self, 
        task: Dict[str, Any], 
        email_content: EmailContentModel
    ) -> str:
        """Build prompt for meeting prep generation."""
        return f"""
        Generate a meeting preparation document for the following meeting:
        
        Meeting: {task['title']}
        Description: {task['description']}
        
        Email Context:
        Subject: {email_content.subject}
        Body: {email_content.body}
        
        Please provide:
        1. Context Summary (2-3 sentences)
        2. Key Talking Points (3-5 bullet points)
        3. Questions to Ask (3-5 questions)
        4. Potential Risks or Concerns (2-3 items)
        
        Format as JSON with keys: context_summary, talking_points, questions, risks
        """
    
    def _parse_prep_response(self, response: str, task: Dict[str, Any]) -> MeetingPrepDocument:
        """Parse LLM response into MeetingPrepDocument."""
        import json
        data = json.loads(response)
        return MeetingPrepDocument(
            meeting_title=task['title'],
            meeting_time=task['deadline'],
            context_summary=data['context_summary'],
            talking_points=data['talking_points'],
            questions=data['questions'],
            risks=data['risks']
        )

class MeetingPrepDocument(BaseModel):
    meeting_title: str
    meeting_time: datetime
    context_summary: str
    talking_points: List[str]
    questions: List[str]
    risks: List[str]
```

#### Orchestration Layer (`services/orchestrator.py`)

Coordinates all services for the `/run-agent` endpoint.

```python
from typing import List, Dict, Any
from datetime import datetime

class AgentOrchestrator:
    def __init__(
        self,
        extraction_service: TaskExtractionService,
        post_processing_service: PostProcessingService,
        calendar_service: CalendarService,
        meeting_prep_service: MeetingPrepService
    ):
        self.extraction = extraction_service
        self.post_processing = post_processing_service
        self.calendar = calendar_service
        self.meeting_prep = meeting_prep_service
    
    def run_agent(self, request: RunAgentRequestModel) -> RunAgentResponseModel:
        """
        Orchestrate the full agent execution flow.
        """
        logs = []
        errors = []
        stats = FeedbackStatsModel(
            tasks_extracted=0,
            calendar_blocks_created=0,
            scheduling_conflicts=0,
            manual_review_items=0
        )
        
        try:
            # Step 1: Extract tasks
            logs.append(LogEntry(timestamp=datetime.now(), message="Extracting tasks from email"))
            raw_tasks = self.extraction.extract_tasks(request.email_content)
            stats.tasks_extracted = len(raw_tasks)
            
            # Step 2: Post-process tasks
            logs.append(LogEntry(timestamp=datetime.now(), message="Post-processing tasks"))
            processed_tasks = self.post_processing.process_tasks(raw_tasks, datetime.now())
            
            # Step 3: Schedule tasks and generate prep docs
            final_tasks = []
            for task in processed_tasks:
                # Check confidence threshold
                if task['confidence'] < 0.7:
                    task['state'] = 'manual_review'
                    stats.manual_review_items += 1
                    logs.append(LogEntry(
                        timestamp=datetime.now(), 
                        message=f"Task '{task['title']}' marked for manual review (confidence: {task['confidence']})"
                    ))
                else:
                    # Try to schedule
                    block_id, error = self.calendar.find_slot_and_create_block(
                        task, 
                        request.calendar_id
                    )
                    
                    if error == "scheduling_conflict":
                        task['state'] = 'scheduling_conflict'
                        stats.scheduling_conflicts += 1
                        logs.append(LogEntry(
                            timestamp=datetime.now(),
                            message=f"Scheduling conflict for task '{task['title']}'"
                        ))
                    else:
                        task['calendar_block_id'] = block_id
                        task['state'] = 'scheduled'
                        stats.calendar_blocks_created += 1
                        logs.append(LogEntry(
                            timestamp=datetime.now(),
                            message=f"Created calendar block for task '{task['title']}'"
                        ))
                    
                    # Generate meeting prep if applicable
                    prep_doc = self.meeting_prep.detect_and_generate_prep(
                        task, 
                        request.email_content
                    )
                    if prep_doc:
                        task['meeting_prep'] = prep_doc
                        logs.append(LogEntry(
                            timestamp=datetime.now(),
                            message=f"Generated meeting prep for '{task['title']}'"
                        ))
                
                final_tasks.append(task)
            
            return RunAgentResponseModel(
                tasks=final_tasks,
                stats=stats,
                logs=logs,
                errors=errors
            )
            
        except Exception as e:
            errors.append(ErrorDetail(
                code="AGENT_EXECUTION_ERROR",
                message=str(e),
                context={"step": "orchestration"}
            ))
            return RunAgentResponseModel(
                tasks=[],
                stats=stats,
                logs=logs,
                errors=errors
            )
```

## Data Models

### Task Data Model

```python
class Task:
    id: str                    # UUID
    title: str                 # Max 200 chars
    description: str           # Max 2000 chars
    deadline: datetime         # ISO 8601 format
    owner: str                 # Email or name
    confidence: float          # 0.0 to 1.0
    priority: Priority         # low, medium, high
    state: TaskState           # scheduled, manual_review, scheduling_conflict, discarded
    calendar_block_id: Optional[str]  # Google Calendar event ID
    source_snippet: str        # Original email text (max 500 chars)
    meeting_prep: Optional[MeetingPrepDocument]
```

### Email Content Data Model

```python
class EmailContent:
    subject: str
    body: str                  # Full email body including HTML
    sender: str                # Email address
    timestamp: str             # ISO 8601 format
    thread_messages: List[ThreadMessage]
    forwarded_messages: List[ForwardedMessage]

class ThreadMessage:
    sender: str
    timestamp: str
    body: str

class ForwardedMessage:
    original_sender: str
    original_timestamp: str
    body: str
```

### Meeting Prep Document Data Model

```python
class MeetingPrepDocument:
    meeting_title: str
    meeting_time: datetime
    context_summary: str       # 2-3 sentences
    talking_points: List[str]  # 3-5 items
    questions: List[str]       # 3-5 items
    risks: List[str]           # 2-3 items
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After analyzing all acceptance criteria, I've identified the following redundancies and consolidations:

**Redundant Properties:**
- Requirements 2.3-2.8 (individual field validation) can be consolidated into a single comprehensive validation property
- Requirements 8.3-8.8 (individual field display) can be consolidated into a single display completeness property
- Requirements 9.5-9.7 are redundant with 8.10 (no editing of titles/descriptions/owners)
- Requirements 4.6 and 4.8 express the same constraint (no scheduling after deadline)
- Requirements 10.2-10.5 (individual stat counts) can be consolidated into a single stats accuracy property
- Requirements 14.1 and 14.2 both test statelessness and can be combined

**Properties to Combine:**
- DOM extraction properties (1.2-1.5) can be combined into a comprehensive extraction property
- Meeting prep document field properties (6.3-6.6) can be combined into a single completeness property
- Calendar block duration constraints (4.3-4.4, 5.4) can be combined into a single invariant

**Unique Properties Retained:**
- Email thread and forwarded message extraction (distinct from basic extraction)
- Priority assignment rules (deadline-based and keyword-based are separate rules)
- Slot finding algorithm (nearest slot selection)
- Confidence-based manual review threshold
- Timeline grouping logic
- Language preservation in multi-language support

### Correctness Properties

Property 1: Complete Email Field Extraction
*For any* Gmail email DOM structure, when extraction is performed, all required fields (subject, body, sender, timestamp) should be successfully extracted and non-empty
**Validates: Requirements 1.2, 1.3, 1.4, 1.5**

Property 2: Thread Message Extraction Completeness
*For any* email thread with N messages, extraction should return exactly N thread messages with complete data
**Validates: Requirements 1.6**

Property 3: Forwarded Message Extraction
*For any* email containing forwarded messages, all forwarded message sections should be extracted with original sender, timestamp, and body
**Validates: Requirements 1.7**

Property 4: Task Structure Validation
*For any* LLM response claiming to contain tasks, validation should accept only responses where every task has all required fields (title, description, deadline, owner, confidence, source_snippet) and confidence is between 0 and 1
**Validates: Requirements 2.3, 2.4, 2.5, 2.6, 2.7, 2.8**

Property 5: Deadline-Based Priority Assignment
*For any* task with a deadline less than 24 hours from current time, the priority should be assigned as High
**Validates: Requirements 3.1**

Property 6: Keyword-Based Priority Elevation
*For any* task where the title or description contains urgent keywords ("urgent", "asap", "immediately", "critical", "emergency"), the priority should be elevated
**Validates: Requirements 3.2**

Property 7: Relative Deadline Resolution
*For any* task with a relative deadline reference (e.g., "tomorrow", "next week", "in 3 days"), the resolved deadline should be an absolute datetime that correctly represents the relative reference from the current time
**Validates: Requirements 3.3**

Property 8: Calendar Slot Duration Invariant
*For any* calendar slot returned by the slot-finding algorithm, the duration should be at least 30 minutes and at most 60 minutes
**Validates: Requirements 4.3, 4.4, 5.4**

Property 9: Nearest Slot Selection
*For any* calendar with multiple available slots before a deadline, the selected slot should be the one with the earliest start time
**Validates: Requirements 4.5**

Property 10: Deadline Constraint Enforcement
*For any* task and calendar configuration, if a calendar block is created, the block's end time must be before or equal to the task deadline
**Validates: Requirements 4.6, 4.8**

Property 11: Calendar Block Title Preservation
*For any* task that gets scheduled, the created calendar block's title should exactly match the task title
**Validates: Requirements 5.2**

Property 12: Calendar Block Description Inclusion
*For any* task that gets scheduled, the created calendar block's description should contain the task description and source snippet
**Validates: Requirements 5.3**

Property 13: Meeting Detection by Keywords
*For any* task where the title or description contains meeting keywords ("meeting", "call", "discussion", "sync", "standup", "review", "demo", "presentation", "interview"), the task should be detected as a meeting
**Validates: Requirements 6.1**

Property 14: Meeting Prep Document Completeness
*For any* generated meeting prep document, it should contain all required sections: context_summary, talking_points, questions, and risks, with each section being non-empty
**Validates: Requirements 6.3, 6.4, 6.5, 6.6**

Property 15: Low Confidence Manual Review Threshold
*For any* task with a confidence score below 0.7, the task state should be set to Manual_Review_State
**Validates: Requirements 7.1**

Property 16: Manual Review Tasks Not Auto-Scheduled
*For any* task in Manual_Review_State, no calendar block should be created automatically
**Validates: Requirements 7.4**

Property 17: Timeline Grouping Correctness
*For any* set of tasks, when grouped by timeline, tasks with deadlines today should be in the "Today" group, tasks with deadlines tomorrow should be in the "Tomorrow" group, and all other future tasks should be in the "Upcoming" group
**Validates: Requirements 8.2**

Property 18: Task Display Completeness
*For any* task displayed in the UI, all required fields (title, description, deadline, owner, confidence, priority) should be visible in the rendered output
**Validates: Requirements 8.3, 8.4, 8.5, 8.6, 8.7, 8.8**

Property 19: CSV Export Field Completeness
*For any* CSV export of tasks, each row should contain all required fields: title, description, deadline, owner, priority, and confidence
**Validates: Requirements 11.3**

Property 20: Language Preservation in Task Extraction
*For any* email in a non-English language, the extracted task fields should preserve the original language without translation
**Validates: Requirements 12.2**

Property 21: Feedback Stats Accuracy
*For any* agent execution, the displayed stats (tasks extracted, calendar blocks created, scheduling conflicts, manual review items) should exactly match the actual counts from the execution
**Validates: Requirements 10.2, 10.3, 10.4, 10.5**

Property 22: Request Statelessness
*For any* two consecutive requests to the backend, the second request's processing should not be influenced by any state from the first request
**Validates: Requirements 14.1, 14.2**

## Error Handling

### Error Categories

1. **Extraction Errors**
   - Invalid JSON from LLM (retry once, then fail)
   - Missing required fields in task data
   - DOM extraction failures (malformed Gmail HTML)

2. **Validation Errors**
   - Invalid request body (Pydantic validation)
   - Confidence score out of range
   - Invalid deadline format

3. **Calendar Errors**
   - Google Calendar API failures
   - Authentication/authorization errors
   - Scheduling conflicts (no available slots)
   - Calendar block creation failures

4. **LLM Errors**
   - API rate limits
   - Timeout errors
   - Invalid responses

### Error Response Format

All errors returned to the Extension follow this structure:

```python
class ErrorDetail(BaseModel):
    code: str              # Machine-readable error code
    message: str           # Human-readable error message
    context: Optional[Dict[str, Any]]  # Additional context for debugging
```

### Error Codes

- `EXTRACTION_FAILED`: LLM task extraction failed after retries
- `VALIDATION_ERROR`: Request validation failed
- `CALENDAR_API_ERROR`: Google Calendar API error
- `SCHEDULING_CONFLICT`: No available slots before deadline
- `CALENDAR_BLOCK_CREATION_FAILED`: Failed to create calendar event
- `LLM_TIMEOUT`: LLM request timed out
- `LLM_RATE_LIMIT`: LLM API rate limit exceeded
- `AGENT_EXECUTION_ERROR`: General orchestration error

### Error Handling Strategy

1. **Retry Logic**: Only for LLM JSON parsing failures (1 retry)
2. **Graceful Degradation**: Continue processing other tasks if one fails
3. **Detailed Logging**: Log all errors with timestamp, context, and stack trace
4. **User-Friendly Messages**: Translate technical errors to actionable user guidance
5. **No Silent Failures**: All errors must be logged and reported to Extension

### Error Recovery

- **Extraction Failures**: Return empty task list with error details
- **Scheduling Conflicts**: Mark task as `scheduling_conflict` state, continue processing
- **Calendar API Failures**: Mark affected tasks with error state, continue processing other tasks
- **Validation Errors**: Return 422 status with detailed validation errors

## Testing Strategy

### Dual Testing Approach

This system requires both unit tests and property-based tests for comprehensive coverage:

- **Unit Tests**: Verify specific examples, edge cases, error conditions, and integration points
- **Property Tests**: Verify universal properties across all inputs through randomization

### Unit Testing Focus

Unit tests should cover:
- Specific examples demonstrating correct behavior (e.g., extracting a known email format)
- Integration points between components (e.g., Extension ↔ Backend API)
- Edge cases (empty emails, malformed JSON, calendar API failures)
- Error conditions (LLM timeouts, validation failures, scheduling conflicts)
- UI rendering (button injection, task board display, feedback panel)

### Property-Based Testing Configuration

**Library Selection**:
- **Python Backend**: Use `hypothesis` for property-based testing
- **TypeScript Extension**: Use `fast-check` for property-based testing

**Test Configuration**:
- Minimum 100 iterations per property test
- Each property test must reference its design document property
- Tag format: `# Feature: ai-execution-agent, Property {number}: {property_text}`

**Property Test Implementation**:
- Each correctness property listed above must be implemented as a single property-based test
- Use generators to create random valid inputs (emails, tasks, calendar configurations)
- Verify the property holds across all generated inputs

### Test Coverage Requirements

**Backend Tests**:
1. Task extraction service tests
   - Property tests for validation (Property 4)
   - Unit tests for LLM integration and retry logic
   - Edge cases: empty emails, malformed JSON, missing fields

2. Post-processing service tests
   - Property tests for priority assignment (Properties 5, 6)
   - Property tests for deadline resolution (Property 7)
   - Edge cases: ambiguous deadlines, extreme dates

3. Calendar service tests
   - Property tests for slot finding (Properties 8, 9, 10)
   - Property tests for block creation (Properties 11, 12)
   - Unit tests for Google Calendar API integration
   - Edge cases: fully booked calendars, deadlines in the past

4. Meeting prep service tests
   - Property tests for meeting detection (Property 13)
   - Property tests for document completeness (Property 14)
   - Unit tests for LLM integration

5. Orchestration tests
   - Property tests for manual review threshold (Property 15, 16)
   - Property tests for statelessness (Property 22)
   - Unit tests for error handling and logging
   - Integration tests for full execution flow

**Extension Tests**:
1. DOM extraction tests
   - Property tests for field extraction (Properties 1, 2, 3)
   - Unit tests for various Gmail HTML structures
   - Edge cases: threads, forwarded messages, unusual formats

2. UI rendering tests
   - Property tests for timeline grouping (Property 17)
   - Property tests for display completeness (Property 18)
   - Unit tests for task board, feedback panel, log display
   - Edge cases: empty task lists, long text fields

3. Export functionality tests
   - Property tests for CSV completeness (Property 19)
   - Unit tests for PDF generation
   - Edge cases: special characters, large datasets

4. Multi-language tests
   - Property tests for language preservation (Property 20)
   - Unit tests for various language inputs
   - Edge cases: mixed-language emails, RTL languages

5. API client tests
   - Unit tests for request/response handling
   - Unit tests for error handling
   - Edge cases: network failures, timeout errors

### Testing Anti-Patterns to Avoid

- Don't write excessive unit tests for cases covered by property tests
- Don't test implementation details (e.g., specific LLM prompts)
- Don't test external services directly (use mocks for Google Calendar API, LLM APIs)
- Don't skip property tests in favor of only unit tests

### Test Data Generation

**For Property Tests**:
- Generate random email content with varying structures
- Generate random task data with various deadlines, priorities, confidence scores
- Generate random calendar configurations with varying event densities
- Generate random multi-language text

**For Unit Tests**:
- Use realistic email examples from Gmail
- Use edge case inputs (empty strings, extreme dates, special characters)
- Use known error conditions (API failures, timeouts)

### Continuous Testing

- Run all tests on every commit
- Property tests should use fixed random seeds for reproducibility
- Track test execution time and optimize slow tests
- Maintain test coverage above 80% for critical paths
