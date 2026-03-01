"""Meeting prep service for meeting detection and document generation."""

from typing import Dict, Any, Optional, List

from models.models import EmailContentModel, MeetingPrepDocument
from src.services.llm_client import LLMClient


class MeetingPrepService:
    """Service for meeting detection and prep document generation."""

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
        return f"""Generate a meeting preparation document for the following meeting:

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

    def _parse_prep_response(
        self,
        response: str,
        task: Dict[str, Any]
    ) -> MeetingPrepDocument:
        """Parse LLM response into MeetingPrepDocument."""
        import json

        # Try to find JSON in response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
        else:
            data = json.loads(response)

        return MeetingPrepDocument(
            meeting_title=task['title'],
            meeting_time=task['deadline'],
            context_summary=data['context_summary'],
            talking_points=data['talking_points'],
            questions=data['questions'],
            risks=data['risks']
        )
