"""
Property-based tests for meeting detection.

Feature: ai-execution-agent, Property 13: Meeting Detection by Keywords
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hypothesis import given, strategies as st, settings
from src.services.meeting_prep import MeetingPrepService
from unittest.mock import Mock


# Strategy for generating tasks with meeting keywords
MEETING_KEYWORDS = [
    "meeting", "call", "discussion", "sync", "standup",
    "review", "demo", "presentation", "interview"
]


@st.composite
def task_with_meeting_keyword(draw):
    """Generate a task that contains at least one meeting keyword."""
    keyword = draw(st.sampled_from(MEETING_KEYWORDS))
    
    # Randomly place keyword in title or description
    place_in_title = draw(st.booleans())
    
    if place_in_title:
        # Generate title with keyword
        prefix = draw(st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')), min_size=0, max_size=20))
        suffix = draw(st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')), min_size=0, max_size=20))
        title = f"{prefix} {keyword} {suffix}".strip()
        description = draw(st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')), min_size=0, max_size=100))
    else:
        # Generate description with keyword
        title = draw(st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')), min_size=0, max_size=50))
        prefix = draw(st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')), min_size=0, max_size=20))
        suffix = draw(st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')), min_size=0, max_size=20))
        description = f"{prefix} {keyword} {suffix}".strip()
    
    return {
        "title": title if title else "Task",
        "description": description if description else "Description"
    }


@st.composite
def task_without_meeting_keyword(draw):
    """Generate a task that does not contain any meeting keywords."""
    # Generate text that doesn't contain meeting keywords
    title = draw(st.text(
        alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'), blacklist_characters=''.join(MEETING_KEYWORDS)),
        min_size=1,
        max_size=50
    ))
    description = draw(st.text(
        alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'), blacklist_characters=''.join(MEETING_KEYWORDS)),
        min_size=1,
        max_size=100
    ))
    
    # Ensure no meeting keywords are present (case-insensitive)
    text = f"{title} {description}".lower()
    if any(keyword in text for keyword in MEETING_KEYWORDS):
        # Fallback to safe non-meeting text
        title = "Fix bug in production"
        description = "Update code to resolve issue"
    
    return {
        "title": title,
        "description": description
    }


class TestPropertyMeetingDetection:
    """Property-based tests for meeting detection."""

    @given(task_with_meeting_keyword())
    @settings(max_examples=100)
    def test_meeting_detection_with_keywords(self, task):
        """
        Property 13: Meeting Detection by Keywords
        
        For any task where the title or description contains meeting keywords,
        the task should be detected as a meeting.
        
        Validates: Requirements 6.1
        """
        # Feature: ai-execution-agent, Property 13: Meeting Detection by Keywords
        
        mock_llm = Mock()
        service = MeetingPrepService(llm_client=mock_llm)
        
        result = service._is_meeting(task)
        
        # Verify that task with meeting keyword is detected as meeting
        assert result is True, (
            f"Task with meeting keyword should be detected as meeting. "
            f"Title: '{task['title']}', Description: '{task['description']}'"
        )

    @given(task_without_meeting_keyword())
    @settings(max_examples=100)
    def test_meeting_detection_without_keywords(self, task):
        """
        Property 13: Meeting Detection by Keywords (negative case)
        
        For any task where the title or description does not contain meeting keywords,
        the task should not be detected as a meeting.
        
        Validates: Requirements 6.1
        """
        # Feature: ai-execution-agent, Property 13: Meeting Detection by Keywords
        
        mock_llm = Mock()
        service = MeetingPrepService(llm_client=mock_llm)
        
        # Verify no meeting keywords are present
        text = f"{task['title']} {task['description']}".lower()
        has_keyword = any(keyword in text for keyword in MEETING_KEYWORDS)
        
        if not has_keyword:
            result = service._is_meeting(task)
            
            # Verify that task without meeting keyword is not detected as meeting
            assert result is False, (
                f"Task without meeting keyword should not be detected as meeting. "
                f"Title: '{task['title']}', Description: '{task['description']}'"
            )
