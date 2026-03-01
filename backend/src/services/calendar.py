"""Calendar service for Google Calendar integration and slot finding."""

# Force reload - updated 2026-02-28 14:06

from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any, TYPE_CHECKING
import os

if TYPE_CHECKING:
    from google.oauth2.credentials import Credentials

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False


class CalendarService:
    """Service for Google Calendar integration and slot finding."""

    MIN_BLOCK_DURATION_MINUTES = 30
    MAX_BLOCK_DURATION_MINUTES = 60
    DEFAULT_BLOCK_DURATION_MINUTES = 45

    def __init__(self, credentials: Optional['Credentials'] = None):
        self.credentials = credentials
        self.service = None
        if credentials and GOOGLE_API_AVAILABLE:
            self.service = build('calendar', 'v3', credentials=credentials)

    def find_slot_and_create_block(
        self,
        task: Dict[str, Any],
        calendar_id: str = "primary",
        user_timezone: str = "UTC"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Find available slot and create calendar block.
        Returns (calendar_block_id, error_message).
        If no slot found before deadline, returns (None, "scheduling_conflict").
        """
        if not self.service:
            return None, "calendar_api_not_available"

        deadline = task["deadline"]
        current_time = datetime.now()
        
        # Ensure both datetimes are timezone-naive for comparison
        if deadline.tzinfo is not None:
            deadline = deadline.replace(tzinfo=None)
        if current_time.tzinfo is not None:
            current_time = current_time.replace(tzinfo=None)

        # Query existing events
        events = self._get_events(calendar_id, current_time, deadline)

        # Find available slot
        slot = self._find_nearest_available_slot(events, current_time, deadline)

        if slot is None:
            return None, "scheduling_conflict"

        # Create calendar block
        block_id = self._create_calendar_block(calendar_id, task, slot, user_timezone)
        return block_id, None

    def _get_events(
        self,
        calendar_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict]:
        """Query Google Calendar API for events in time range."""
        if not self.service:
            return []

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
        # Make start_time and deadline timezone-naive for comparison
        if start_time.tzinfo is not None:
            start_time = start_time.replace(tzinfo=None)
        if deadline.tzinfo is not None:
            deadline = deadline.replace(tzinfo=None)

        # Sort events by start time
        sorted_events = sorted(
            events,
            key=lambda e: self._parse_event_time(e['start'])
        )

        # If no events, check if we can fit a slot from start_time
        if not sorted_events:
            duration = (deadline - start_time).total_seconds() / 60
            if duration >= self.MIN_BLOCK_DURATION_MINUTES:
                slot_end = min(
                    start_time + timedelta(minutes=self.DEFAULT_BLOCK_DURATION_MINUTES),
                    deadline
                )
                return (start_time, slot_end)
            return None

        # Check gap before first event
        first_event_start = self._parse_event_time(sorted_events[0]['start'])
        if first_event_start.tzinfo is not None:
            first_event_start = first_event_start.replace(tzinfo=None)
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
            
            if current_event_end.tzinfo is not None:
                current_event_end = current_event_end.replace(tzinfo=None)
            if next_event_start.tzinfo is not None:
                next_event_start = next_event_start.replace(tzinfo=None)
            
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
        last_event_end = self._parse_event_time(sorted_events[-1]['end'])
        if last_event_end.tzinfo is not None:
            last_event_end = last_event_end.replace(tzinfo=None)
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
        slot: Tuple[datetime, datetime],
        user_timezone: str = 'UTC'
    ) -> str:
        """Create calendar event and return event ID."""
        if not self.service:
            raise RuntimeError("Calendar service not initialized")

        # Use user's timezone if provided, otherwise UTC
        timezone = user_timezone if user_timezone else 'UTC'
        
        event = {
            'summary': task['title'],
            'description': f"{task['description']}\n\nSource: {task['source_snippet']}",
            'start': {
                'dateTime': slot[0].isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': slot[1].isoformat(),
                'timeZone': timezone,
            },
        }

        print(f"Creating calendar event on calendar: {calendar_id}")
        print(f"Event: {task['title']}")
        print(f"Start: {slot[0].isoformat()} ({timezone})")
        print(f"End: {slot[1].isoformat()} ({timezone})")
        
        created_event = self.service.events().insert(
            calendarId=calendar_id,
            body=event
        ).execute()
        
        event_link = created_event.get('htmlLink', 'No link')
        print(f"✓ Created event ID: {created_event['id']}")
        print(f"✓ View at: {event_link}")

        return created_event['id']

    def _parse_event_time(self, time_dict: Dict) -> datetime:
        """Parse event time from Google Calendar API response."""
        time_str = time_dict.get('dateTime') or time_dict.get('date')
        if time_str is None:
            raise ValueError("Invalid time format in event")
        return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
