"""Task extraction service with LLM integration."""

from typing import List, Dict, Any, Optional
import json
import re
import uuid

from models.models import EmailContentModel
from src.services.llm_client import LLMClient


class ExtractionError(Exception):
    """Custom exception for extraction failures."""
    pass


class TaskExtractionService:
    """Service for extracting tasks from email content using LLM."""

    def __init__(self, llm_client: LLMClient, max_retries: int = 1):
        self.llm_client = llm_client
        self.max_retries = max_retries

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
                tasks = self._parse_json_response(response)
                validated_tasks = self._validate_task_structure(tasks)
                return validated_tasks
            except (json.JSONDecodeError, ExtractionError) as e:
                if attempt == self.max_retries:
                    raise ExtractionError(f"Failed to extract tasks: {str(e)}")

        return []

    def _build_extraction_prompt(self, email_content: EmailContentModel) -> str:
        """
        Build structured prompt for LLM task extraction.
        Includes multi-language support configuration.
        """
        thread_context = ""
        if email_content.thread_messages:
            thread_context = "\n\nThread Messages:\n" + "\n---\n".join(
                f"From: {msg.sender}\nTime: {msg.timestamp}\nContent: {msg.body}"
                for msg in email_content.thread_messages
            )

        forwarded_context = ""
        if email_content.forwarded_messages:
            forwarded_context = "\n\nForwarded Messages:\n" + "\n---\n".join(
                f"From: {msg.original_sender}\nTime: {msg.original_timestamp}\nContent: {msg.body}"
                for msg in email_content.forwarded_messages
            )

        return f"""Extract actionable tasks from the following email content.

Email Subject: {email_content.subject}
Email Body: {email_content.body}
Sender: {email_content.sender}
Timestamp: {email_content.timestamp}
{thread_context}
{forwarded_context}

Please identify all actionable tasks and return them as a JSON array with the following structure:
[
  {{
    "id": "unique_task_id",
    "title": "concise task title",
    "description": "detailed task description",
    "deadline": "ISO 8601 deadline (e.g., 2024-03-15T14:00:00Z or relative like 'tomorrow 3pm')",
    "owner": "email address or name of responsible person",
    "confidence": 0.0 to 1.0,
    "source_snippet": "relevant excerpt from email"
  }}
]

Rules:
1. Each task must have all required fields
2. Confidence score reflects extraction certainty (0.0-1.0)
3. If deadline is relative, use natural language (e.g., "tomorrow", "next week", "in 3 days")
4. Preserve the original language of the email in task fields
5. If no tasks are found, return an empty array []

Return ONLY valid JSON, no additional text."""

    def _parse_json_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response and extract JSON array."""
        # Try to find JSON in response
        json_match = re.search(r'\[\s*{.*?}\s*\]', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        # Try parsing entire response as JSON
        return json.loads(response)

    def _validate_task_structure(self, tasks: List[Dict]) -> List[Dict]:
        """
        Validate that each task has required fields:
        - title, description, deadline, owner, confidence, source_snippet
        Generate ID if missing.
        """
        required_fields = ['title', 'description', 'deadline', 'owner', 'confidence', 'source_snippet']

        for i, task in enumerate(tasks):
            # Generate ID if missing
            if 'id' not in task or not task['id']:
                task['id'] = f"task-{uuid.uuid4().hex[:8]}"
            
            for field in required_fields:
                if field not in task:
                    raise ExtractionError(f"Task {i+1} missing required field: {field}")

            # Validate confidence score
            confidence = task.get('confidence')
            if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                raise ExtractionError(f"Task {i+1} has invalid confidence score: {confidence}")

        return tasks
