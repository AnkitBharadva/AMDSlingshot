"""Direct test of Google Calendar API to verify it's working."""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import json

# Load credentials
creds = Credentials.from_authorized_user_file('token.json')
service = build('calendar', 'v3', credentials=creds)

# Create a test event
now = datetime.now()
event = {
    'summary': 'TEST EVENT - AI Agent',
    'description': 'This is a test event to verify calendar API is working',
    'start': {
        'dateTime': now.isoformat(),
        'timeZone': 'America/New_York',
    },
    'end': {
        'dateTime': (now + timedelta(minutes=30)).isoformat(),
        'timeZone': 'America/New_York',
    },
}

print(f"Creating test event at {now}")
print(f"Calendar ID: chhagaan003@gmail.com")

try:
    created_event = service.events().insert(
        calendarId='chhagaan003@gmail.com',
        body=event
    ).execute()
    
    print(f"\n✓ SUCCESS! Event created:")
    print(f"  Event ID: {created_event['id']}")
    print(f"  Link: {created_event.get('htmlLink', 'No link')}")
    print(f"\nGo to Google Calendar and check if you see 'TEST EVENT - AI Agent'")
    
except Exception as e:
    print(f"\n✗ FAILED: {e}")
