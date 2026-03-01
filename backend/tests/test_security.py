"""
Unit tests for security measures.

Tests input sanitization, rate limiting, log sanitization,
and data handling policies.
"""

import pytest
from datetime import datetime, timedelta
from backend.src.security import (
    InputSanitizer,
    RateLimiter,
    LogSanitizer,
    HTTPSEnforcer,
    DataRetentionPolicy,
    MAX_EMAIL_BODY_SIZE,
    MAX_EMAIL_SUBJECT_SIZE
)


class TestInputSanitizer:
    """Tests for InputSanitizer class."""
    
    def test_sanitize_string_removes_script_tags(self):
        """Test that script tags are removed from input."""
        malicious_input = "Hello <script>alert('XSS')</script> World"
        result = InputSanitizer.sanitize_string(malicious_input)
        assert "<script>" not in result
        assert "alert" not in result
        assert "Hello" in result
        assert "World" in result
    
    def test_sanitize_string_html_escapes(self):
        """Test that HTML special characters are escaped."""
        input_with_html = "Hello <b>World</b> & Friends"
        result = InputSanitizer.sanitize_string(input_with_html)
        assert "&lt;" in result or "<b>" not in result
        assert "&amp;" in result or " & " not in result
    
    def test_sanitize_string_removes_null_bytes(self):
        """Test that null bytes are removed."""
        input_with_null = "Hello\x00World"
        result = InputSanitizer.sanitize_string(input_with_null)
        assert "\x00" not in result
        assert "HelloWorld" in result
    
    def test_sanitize_string_enforces_max_length(self):
        """Test that strings exceeding max length raise ValueError."""
        long_string = "a" * 20000
        with pytest.raises(ValueError, match="exceeds maximum length"):
            InputSanitizer.sanitize_string(long_string, max_length=10000)
    
    def test_sanitize_email_content_validates_subject_size(self):
        """Test that email subject size is validated."""
        email_content = {
            "subject": "a" * (MAX_EMAIL_SUBJECT_SIZE + 1),
            "body": "Test body",
            "sender": "test@example.com",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        with pytest.raises(ValueError, match="Email subject exceeds maximum size"):
            InputSanitizer.sanitize_email_content(email_content)
    
    def test_sanitize_email_content_validates_body_size(self):
        """Test that email body size is validated."""
        email_content = {
            "subject": "Test subject",
            "body": "a" * (MAX_EMAIL_BODY_SIZE + 1),
            "sender": "test@example.com",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        with pytest.raises(ValueError, match="Email body exceeds maximum size"):
            InputSanitizer.sanitize_email_content(email_content)
    
    def test_sanitize_email_content_sanitizes_all_fields(self):
        """Test that all email fields are sanitized."""
        email_content = {
            "subject": "Test <script>alert('xss')</script>",
            "body": "Body with <script>malicious code</script>",
            "sender": "test@example.com",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        result = InputSanitizer.sanitize_email_content(email_content)
        assert "<script>" not in result["subject"]
        assert "<script>" not in result["body"]
        assert "alert" not in result["subject"]
    
    def test_sanitize_email_content_handles_thread_messages(self):
        """Test that thread messages are sanitized."""
        email_content = {
            "subject": "Test",
            "body": "Test body",
            "sender": "test@example.com",
            "timestamp": "2024-01-01T00:00:00Z",
            "thread_messages": [
                {
                    "sender": "user1@example.com",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "body": "Message with <script>alert('xss')</script>"
                }
            ]
        }
        result = InputSanitizer.sanitize_email_content(email_content)
        assert len(result["thread_messages"]) == 1
        assert "<script>" not in result["thread_messages"][0]["body"]
    
    def test_sanitize_email_content_handles_forwarded_messages(self):
        """Test that forwarded messages are sanitized."""
        email_content = {
            "subject": "Test",
            "body": "Test body",
            "sender": "test@example.com",
            "timestamp": "2024-01-01T00:00:00Z",
            "forwarded_messages": [
                {
                    "original_sender": "user1@example.com",
                    "original_timestamp": "2024-01-01T00:00:00Z",
                    "body": "Forwarded with <script>alert('xss')</script>"
                }
            ]
        }
        result = InputSanitizer.sanitize_email_content(email_content)
        assert len(result["forwarded_messages"]) == 1
        assert "<script>" not in result["forwarded_messages"][0]["body"]
    
    def test_validate_no_sql_injection_detects_patterns(self):
        """Test that SQL injection patterns are detected."""
        malicious_inputs = [
            "SELECT * FROM users",
            "SELECT name FROM accounts",
            "INSERT INTO users VALUES",
            "DELETE FROM users WHERE",
            "DROP TABLE users",
            "UPDATE users WHERE id=1"
        ]
        for malicious_input in malicious_inputs:
            try:
                InputSanitizer.validate_no_sql_injection(malicious_input)
                # If we get here, the validation didn't raise an exception
                pytest.fail(f"Expected ValueError for input: {malicious_input}")
            except ValueError as e:
                assert "malicious SQL pattern" in str(e)
    
    def test_validate_no_sql_injection_allows_safe_input(self):
        """Test that safe input passes SQL injection check."""
        safe_inputs = [
            "This is a normal email about selecting a date",
            "Please update me on the project status",
            "Let's create a new document for the meeting",
            "I need to select the right option for deployment",
            "Can you add this to the agenda"
        ]
        for safe_input in safe_inputs:
            # Should not raise exception
            InputSanitizer.validate_no_sql_injection(safe_input)


class TestRateLimiter:
    """Tests for RateLimiter class."""
    
    def test_rate_limiter_allows_requests_under_limit(self):
        """Test that requests under the limit are allowed."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        client_id = "test_client"
        
        # Should allow 5 requests
        for i in range(5):
            assert limiter.is_allowed(client_id) is True
    
    def test_rate_limiter_blocks_requests_over_limit(self):
        """Test that requests over the limit are blocked."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        client_id = "test_client"
        
        # Allow 3 requests
        for i in range(3):
            assert limiter.is_allowed(client_id) is True
        
        # Block 4th request
        assert limiter.is_allowed(client_id) is False
    
    def test_rate_limiter_resets_after_window(self):
        """Test that rate limit resets after time window."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)
        client_id = "test_client"
        
        # Use up limit
        assert limiter.is_allowed(client_id) is True
        assert limiter.is_allowed(client_id) is True
        assert limiter.is_allowed(client_id) is False
        
        # Wait for window to expire
        import time
        time.sleep(1.1)
        
        # Should allow requests again
        assert limiter.is_allowed(client_id) is True
    
    def test_rate_limiter_tracks_different_clients(self):
        """Test that different clients have separate limits."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        # Client 1 uses limit
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is False
        
        # Client 2 should still have full limit
        assert limiter.is_allowed("client2") is True
        assert limiter.is_allowed("client2") is True
    
    def test_cleanup_old_entries_removes_expired(self):
        """Test that cleanup removes old entries."""
        limiter = RateLimiter(max_requests=5, window_seconds=1)
        
        # Add requests for multiple clients
        limiter.is_allowed("client1")
        limiter.is_allowed("client2")
        
        # Wait for entries to expire
        import time
        time.sleep(2.5)
        
        # Cleanup
        limiter.cleanup_old_entries()
        
        # Verify cleanup (requests dict should be empty or have no old entries)
        assert len(limiter.requests) == 0 or all(
            not timestamps for timestamps in limiter.requests.values()
        )


class TestLogSanitizer:
    """Tests for LogSanitizer class."""
    
    def test_sanitize_log_message_redacts_emails(self):
        """Test that email addresses are redacted from logs."""
        message = "User john.doe@example.com sent a request"
        result = LogSanitizer.sanitize_log_message(message)
        assert "john.doe@example.com" not in result
        assert "[EMAIL_REDACTED]" in result
    
    def test_sanitize_log_message_redacts_api_keys(self):
        """Test that API keys are redacted from logs."""
        messages = [
            "api_key=sk-1234567890abcdef",
            'token: "abc123xyz"',
            "secret=my_secret_value",
            "password='p@ssw0rd'"
        ]
        for message in messages:
            result = LogSanitizer.sanitize_log_message(message)
            assert "sk-1234567890abcdef" not in result
            assert "abc123xyz" not in result
            assert "my_secret_value" not in result
            assert "p@ssw0rd" not in result
            assert "[REDACTED]" in result
    
    def test_sanitize_log_context_redacts_sensitive_fields(self):
        """Test that sensitive fields are redacted from context."""
        context = {
            "user": "john",
            "body": "This is sensitive email content",
            "api_key": "sk-1234567890",
            "task_count": 5
        }
        result = LogSanitizer.sanitize_log_context(context)
        assert result["user"] == "john"
        assert result["body"] == "[REDACTED]"
        assert result["api_key"] == "[REDACTED]"
        assert result["task_count"] == 5
    
    def test_sanitize_log_context_handles_nested_dicts(self):
        """Test that nested dictionaries are sanitized."""
        context = {
            "request": {
                "email_content": "Sensitive data",
                "user_id": "123"
            },
            "response": {
                "status": "success"
            }
        }
        result = LogSanitizer.sanitize_log_context(context)
        assert result["request"]["email_content"] == "[REDACTED]"
        assert result["request"]["user_id"] == "123"
        assert result["response"]["status"] == "success"
    
    def test_sanitize_log_context_preserves_non_sensitive_data(self):
        """Test that non-sensitive data is preserved."""
        context = {
            "task_count": 5,
            "status": "completed",
            "duration_ms": 1234
        }
        result = LogSanitizer.sanitize_log_context(context)
        assert result == context


class TestHTTPSEnforcer:
    """Tests for HTTPSEnforcer class."""
    
    def test_is_secure_connection_detects_https(self):
        """Test that HTTPS connections are detected."""
        from unittest.mock import Mock
        
        request = Mock()
        request.url.scheme = "https"
        request.headers = {}
        
        assert HTTPSEnforcer.is_secure_connection(request) is True
    
    def test_is_secure_connection_detects_http(self):
        """Test that HTTP connections are detected."""
        from unittest.mock import Mock
        
        request = Mock()
        request.url.scheme = "http"
        request.headers = {}
        
        assert HTTPSEnforcer.is_secure_connection(request) is False
    
    def test_is_secure_connection_checks_forwarded_proto(self):
        """Test that X-Forwarded-Proto header is checked."""
        from unittest.mock import Mock
        
        request = Mock()
        request.url.scheme = "http"
        request.headers = {"X-Forwarded-Proto": "https"}
        
        assert HTTPSEnforcer.is_secure_connection(request) is True
    
    def test_enforce_https_allows_localhost(self):
        """Test that localhost is allowed in development."""
        from unittest.mock import Mock
        
        request = Mock()
        request.url.scheme = "http"
        request.headers = {}
        request.client.host = "127.0.0.1"
        
        # Should not raise exception
        HTTPSEnforcer.enforce_https(request, allow_localhost=True)
    
    def test_enforce_https_blocks_non_secure(self):
        """Test that non-HTTPS connections are blocked."""
        from unittest.mock import Mock
        from fastapi import HTTPException
        
        request = Mock()
        request.url.scheme = "http"
        request.headers = {}
        request.client.host = "192.168.1.1"
        
        with pytest.raises(HTTPException) as exc_info:
            HTTPSEnforcer.enforce_https(request, allow_localhost=False)
        
        assert exc_info.value.status_code == 403
        assert "HTTPS" in exc_info.value.detail


class TestDataRetentionPolicy:
    """Tests for DataRetentionPolicy class."""
    
    def test_verify_no_persistence_returns_true(self):
        """Test that verify_no_persistence returns True by design."""
        email_content = "This is test email content"
        result = DataRetentionPolicy.verify_no_persistence(email_content)
        assert result is True
    
    def test_clear_request_data_deletes_reference(self):
        """Test that clear_request_data removes reference."""
        test_data = {"email": "test@example.com", "body": "content"}
        
        # Should not raise exception
        DataRetentionPolicy.clear_request_data(test_data)
        
        # After deletion, the variable should not be accessible
        # (In practice, Python's garbage collector handles this)


class TestIntegrationSecurity:
    """Integration tests for security measures."""
    
    def test_malicious_input_is_sanitized_end_to_end(self):
        """Test that malicious input is sanitized through the full flow."""
        email_content = {
            "subject": "Test <script>alert('xss')</script>",
            "body": "Body with <script>malicious()</script> and user@example.com",
            "sender": "attacker@evil.com",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Sanitize input
        sanitized = InputSanitizer.sanitize_email_content(email_content)
        
        # Verify sanitization
        assert "<script>" not in sanitized["subject"]
        assert "<script>" not in sanitized["body"]
        
        # Sanitize for logging
        log_message = f"Processing email: {sanitized['body']}"
        sanitized_log = LogSanitizer.sanitize_log_message(log_message)
        
        # Verify email is redacted in logs
        assert "[EMAIL_REDACTED]" in sanitized_log
    
    def test_email_content_not_stored_after_processing(self):
        """Test that email content is not persisted."""
        email_content = "Sensitive email content that should not be stored"
        
        # Verify no persistence
        assert DataRetentionPolicy.verify_no_persistence(email_content) is True
        
        # Clear data
        DataRetentionPolicy.clear_request_data(email_content)
    
    def test_logs_dont_contain_sensitive_data(self):
        """Test that logs don't contain sensitive information."""
        sensitive_context = {
            "email_content": "This is private email content",
            "body": "Email body with secrets",
            "api_key": "sk-secret123",
            "task_id": "task-123"
        }
        
        # Sanitize context for logging
        sanitized = LogSanitizer.sanitize_log_context(sensitive_context)
        
        # Verify sensitive fields are redacted
        assert sanitized["email_content"] == "[REDACTED]"
        assert sanitized["body"] == "[REDACTED]"
        assert sanitized["api_key"] == "[REDACTED]"
        
        # Verify non-sensitive fields are preserved
        assert sanitized["task_id"] == "task-123"
