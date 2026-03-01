"""Post-processing service for priority and deadline handling."""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dateutil import parser as date_parser


class PostProcessingService:
    """Service for post-processing extracted tasks."""

    URGENT_KEYWORDS = ["urgent", "asap", "immediately", "critical", "emergency"]
    HIGH_PRIORITY_THRESHOLD_HOURS = 24

    def process_tasks(
        self, tasks: List[Dict[str, Any]], current_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Apply rule-based post-processing to extracted tasks.
        """
        if current_time is None:
            current_time = datetime.now()

        processed = []
        for task in tasks:
            task = self._assign_priority(task, current_time)
            task = self._resolve_deadline(task, current_time)
            processed.append(task)
        return processed

    def _assign_priority(
        self, task: Dict[str, Any], current_time: datetime
    ) -> Dict[str, Any]:
        """
        Rule-based priority assignment:
        - High: deadline < 24 hours OR contains urgent keyword
        - Medium: default
        - Low: deadline is far in the future (more than 7 days)
        """
        deadline = task.get("deadline")
        
        # Handle missing or None deadline
        if deadline is None:
            task["priority"] = "medium"
            return task
            
        if isinstance(deadline, str):
            try:
                deadline = date_parser.parse(deadline)
            except (ValueError, TypeError):
                task["priority"] = "medium"
                return task

        hours_until_deadline = (deadline - current_time).total_seconds() / 3600

        # Check urgent keywords
        text = f"{task.get('title', '')} {task.get('description', '')}".lower()
        has_urgent_keyword = any(keyword in text for keyword in self.URGENT_KEYWORDS)

        # Determine priority
        if hours_until_deadline < self.HIGH_PRIORITY_THRESHOLD_HOURS or has_urgent_keyword:
            task["priority"] = "high"
        elif hours_until_deadline > 168:  # More than 7 days
            task["priority"] = "low"
        else:
            task["priority"] = "medium"

        return task

    def _resolve_deadline(
        self, task: Dict[str, Any], current_time: datetime
    ) -> Dict[str, Any]:
        """
        Resolve relative deadline references to absolute dates.
        Uses python-dateutil for parsing.
        """
        deadline = task.get("deadline")
        
        if deadline is None:
            # If no deadline, set to current time as fallback
            task["deadline"] = current_time
        elif isinstance(deadline, str):
            try:
                # Handle relative references like "tomorrow", "next week", "in 3 days"
                task["deadline"] = date_parser.parse(deadline, default=current_time)
            except (ValueError, TypeError):
                # If parsing fails, set to current time as fallback
                task["deadline"] = current_time
        
        return task
