# AI Execution Agent Backend

Python FastAPI backend for the AI Execution Agent Chrome Extension.

## Setup

1. Create a Python virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp src/.env.example src/.env
# Edit src/.env with your API keys
```

4. Run the server:
```bash
uvicorn src.main:app --reload
```

## Testing

```bash
pytest tests/ -v
```

## API Endpoint

### POST /run-agent

Extracts tasks from email content and schedules them on Google Calendar.

**Request Body:**
```json
{
  "email_content": {
    "subject": "Meeting Request",
    "body": "Can we schedule a meeting?",
    "sender": "user@example.com",
    "timestamp": "2024-03-15T10:00:00Z",
    "thread_messages": [],
    "forwarded_messages": []
  },
  "user_timezone": "America/New_York",
  "calendar_id": "primary"
}
```

**Response:**
```json
{
  "tasks": [...],
  "stats": {
    "tasks_extracted": 1,
    "calendar_blocks_created": 1,
    "scheduling_conflicts": 0,
    "manual_review_items": 0
  },
  "logs": [...],
  "errors": []
}
```
