"""Property-based tests for language preservation in task extraction."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock

from models.models import EmailContentModel, ThreadMessageModel, ForwardedMessageModel
from services.extraction import TaskExtractionService


@given(
    subject=st.text(min_size=1, max_size=200),
    body=st.text(min_size=1, max_size=5000),
    sender=st.emails(),
    timestamp=st.datetimes(),
)
@settings(max_examples=100)
def test_property_20_language_preservation_in_task_extraction(subject, body, sender, timestamp):
    """
    Property 20: Language Preservation in Task Extraction

    For any email content in any language, when the extraction service builds
    the prompt, the original language should be preserved in the prompt.
    """
    email_content = EmailContentModel(
        subject=subject,
        body=body,
        sender=sender,
        timestamp=timestamp.isoformat(),
    )

    # Create extraction service
    mock_llm_client = Mock()
    extraction_service = TaskExtractionService(llm_client=mock_llm_client, max_retries=1)

    # Build the prompt
    prompt = extraction_service._build_extraction_prompt(email_content)

    # Verify that the original subject and body are included in the prompt
    # The prompt should contain the original content for the LLM to process
    assert subject in prompt, "Original subject should be preserved in prompt"
    assert body in prompt, "Original body should be preserved in prompt"


@given(
    thread_messages=st.lists(
        st.fixed_dictionaries({
            'sender': st.emails(),
            'timestamp': st.datetimes(),
            'body': st.text(min_size=1, max_size=1000),
        }),
        min_size=1,
        max_size=5
    )
)
@settings(max_examples=100)
def test_property_20_language_preservation_thread_messages(thread_messages):
    """
    Property 20: Language Preservation in Task Extraction - Thread Messages

    For any email thread with messages in any language, when the extraction
    service builds the prompt, the original language of thread messages
    should be preserved.
    """
    email_content = EmailContentModel(
        subject="Test Subject",
        body="Test Body",
        sender="test@example.com",
        timestamp="2024-03-15T10:00:00Z",
        thread_messages=[
            ThreadMessageModel(
                sender=msg['sender'],
                timestamp=msg['timestamp'].isoformat(),
                body=msg['body']
            )
            for msg in thread_messages
        ]
    )

    # Create extraction service
    mock_llm_client = Mock()
    extraction_service = TaskExtractionService(llm_client=mock_llm_client, max_retries=1)

    # Build the prompt
    prompt = extraction_service._build_extraction_prompt(email_content)

    # Verify that thread message bodies are preserved in the prompt
    for msg in thread_messages:
        assert msg['body'] in prompt, f"Thread message body should be preserved: {msg['body']}"


@given(
    forwarded_messages=st.lists(
        st.fixed_dictionaries({
            'original_sender': st.emails(),
            'original_timestamp': st.datetimes(),
            'body': st.text(min_size=1, max_size=1000),
        }),
        min_size=1,
        max_size=3
    )
)
@settings(max_examples=100)
def test_property_20_language_preservation_forwarded_messages(forwarded_messages):
    """
    Property 20: Language Preservation in Task Extraction - Forwarded Messages

    For any email with forwarded messages in any language, when the extraction
    service builds the prompt, the original language of forwarded messages
    should be preserved.
    """
    email_content = EmailContentModel(
        subject="Test Subject",
        body="Test Body",
        sender="test@example.com",
        timestamp="2024-03-15T10:00:00Z",
        forwarded_messages=[
            ForwardedMessageModel(
                original_sender=msg['original_sender'],
                original_timestamp=msg['original_timestamp'].isoformat(),
                body=msg['body']
            )
            for msg in forwarded_messages
        ]
    )

    # Create extraction service
    mock_llm_client = Mock()
    extraction_service = TaskExtractionService(llm_client=mock_llm_client, max_retries=1)

    # Build the prompt
    prompt = extraction_service._build_extraction_prompt(email_content)

    # Verify that forwarded message bodies are preserved in the prompt
    for msg in forwarded_messages:
        assert msg['body'] in prompt, f"Forwarded message body should be preserved: {msg['body']}"


@given(
    non_english_subject=st.sampled_from([
        "Reunión de Proyecto",  # Spanish
        "会議の予定",  # Japanese
        "Réunion de projet",  # French
        "Projekttreffen",  # German
        "会议邀请",  # Chinese
        "Мtg по проекту",  # Russian
    ]),
    non_english_body=st.text(min_size=1, max_size=500),
)
@settings(max_examples=50)
def test_property_20_language_preservation_non_english(non_english_subject, non_english_body):
    """
    Property 20: Language Preservation in Task Extraction - Non-English Content

    For emails in non-English languages, the original language should be
    preserved in the extraction prompt.
    """
    email_content = EmailContentModel(
        subject=non_english_subject,
        body=non_english_body,
        sender="test@example.com",
        timestamp="2024-03-15T10:00:00Z",
    )

    # Create extraction service
    mock_llm_client = Mock()
    extraction_service = TaskExtractionService(llm_client=mock_llm_client, max_retries=1)

    # Build the prompt
    prompt = extraction_service._build_extraction_prompt(email_content)

    # Verify that non-English content is preserved
    assert non_english_subject in prompt, "Non-English subject should be preserved"
    assert non_english_body in prompt, "Non-English body should be preserved"
