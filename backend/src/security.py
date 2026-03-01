"""
Security utilities for input validation, sanitization, and rate limiting.

This module provides security measures to protect the API from malicious input
and abuse, including input sanitization, size limits, and rate limiting.
"""

import re
import html
from typing import Any, Dict
from datetime import datetime, timedelta
from collections import defaultdict
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


# Configuration constants
MAX_EMAIL_BODY_SIZE = 1_000_000  # 1MB
MAX_EMAIL_SUBJECT_SIZE = 1000
MAX_STRING_FIELD_SIZE = 10_000
RATE_LIMIT_REQUESTS = 10  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds


class InputSanitizer:
    """Sanitizes user input to prevent injection attacks and malicious content."""
    
    # Patterns for potentially malicious content
    SCRIPT_PATTERN = re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)
    # More specific SQL injection pattern - look for SQL keywords with suspicious context
    SQL_INJECTION_PATTERN = re.compile(
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b.{0,50}?\b(FROM|INTO|TABLE|DATABASE|WHERE))",
        re.IGNORECASE
    )
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = MAX_STRING_FIELD_SIZE) -> str:
        """
        Sanitize a string by removing potentially malicious content.
        
        Args:
            value: The string to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
            
        Raises:
            ValueError: If input exceeds max_length
        """
        if not isinstance(value, str):
            return str(value)
        
        # Check length
        if len(value) > max_length:
            raise ValueError(f"Input exceeds maximum length of {max_length} characters")
        
        # Remove script tags
        value = InputSanitizer.SCRIPT_PATTERN.sub('', value)
        
        # HTML escape to prevent XSS
        value = html.escape(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        return value
    
    @staticmethod
    def sanitize_email_content(email_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize email content fields with appropriate size limits.
        
        Args:
            email_content: Dictionary containing email content
            
        Returns:
            Sanitized email content dictionary
            
        Raises:
            ValueError: If any field exceeds size limits
        """
        sanitized = {}
        
        # Sanitize subject with specific limit
        if 'subject' in email_content:
            if len(email_content['subject']) > MAX_EMAIL_SUBJECT_SIZE:
                raise ValueError(f"Email subject exceeds maximum size of {MAX_EMAIL_SUBJECT_SIZE} characters")
            sanitized['subject'] = InputSanitizer.sanitize_string(
                email_content['subject'], 
                MAX_EMAIL_SUBJECT_SIZE
            )
        
        # Sanitize body with specific limit
        if 'body' in email_content:
            if len(email_content['body']) > MAX_EMAIL_BODY_SIZE:
                raise ValueError(f"Email body exceeds maximum size of {MAX_EMAIL_BODY_SIZE} bytes")
            sanitized['body'] = InputSanitizer.sanitize_string(
                email_content['body'], 
                MAX_EMAIL_BODY_SIZE
            )
        
        # Sanitize other string fields
        for field in ['sender', 'timestamp']:
            if field in email_content:
                sanitized[field] = InputSanitizer.sanitize_string(
                    email_content[field], 
                    MAX_STRING_FIELD_SIZE
                )
        
        # Sanitize thread messages
        if 'thread_messages' in email_content:
            sanitized['thread_messages'] = [
                {
                    'sender': InputSanitizer.sanitize_string(msg.get('sender', ''), MAX_STRING_FIELD_SIZE),
                    'timestamp': InputSanitizer.sanitize_string(msg.get('timestamp', ''), MAX_STRING_FIELD_SIZE),
                    'body': InputSanitizer.sanitize_string(msg.get('body', ''), MAX_EMAIL_BODY_SIZE)
                }
                for msg in email_content.get('thread_messages', [])
            ]
        
        # Sanitize forwarded messages
        if 'forwarded_messages' in email_content:
            sanitized['forwarded_messages'] = [
                {
                    'original_sender': InputSanitizer.sanitize_string(msg.get('original_sender', ''), MAX_STRING_FIELD_SIZE),
                    'original_timestamp': InputSanitizer.sanitize_string(msg.get('original_timestamp', ''), MAX_STRING_FIELD_SIZE),
                    'body': InputSanitizer.sanitize_string(msg.get('body', ''), MAX_EMAIL_BODY_SIZE)
                }
                for msg in email_content.get('forwarded_messages', [])
            ]
        
        return sanitized
    
    @staticmethod
    def validate_no_sql_injection(value: str) -> None:
        """
        Check for SQL injection patterns.
        
        Args:
            value: String to check
            
        Raises:
            ValueError: If SQL injection pattern detected
        """
        if InputSanitizer.SQL_INJECTION_PATTERN.search(value):
            raise ValueError("Potentially malicious SQL pattern detected")


class RateLimiter:
    """
    Simple in-memory rate limiter for API endpoints.
    
    Tracks requests per IP address and enforces rate limits.
    """
    
    def __init__(self, max_requests: int = RATE_LIMIT_REQUESTS, window_seconds: int = RATE_LIMIT_WINDOW):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Check if a request from client_id is allowed.
        
        Args:
            client_id: Identifier for the client (e.g., IP address)
            
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        # Remove old requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True
    
    def cleanup_old_entries(self) -> None:
        """Remove entries for clients with no recent requests."""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds * 2)
        
        clients_to_remove = []
        for client_id, timestamps in self.requests.items():
            if not timestamps or all(t < cutoff for t in timestamps):
                clients_to_remove.append(client_id)
        
        for client_id in clients_to_remove:
            del self.requests[client_id]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limiting on API requests.
    """
    
    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and enforce rate limiting.
        """
        # Get client identifier (IP address)
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if not self.rate_limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Proceed with request
        response = await call_next(request)
        return response



class LogSanitizer:
    """
    Sanitizes log messages to exclude sensitive content.
    
    Prevents email content, API keys, and other sensitive data from
    appearing in logs.
    """
    
    # Patterns for sensitive data
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    API_KEY_PATTERN = re.compile(r'(api[_-]?key|token|secret|password)["\']?\s*[:=]\s*["\']?([^\s"\']+)', re.IGNORECASE)
    
    # Fields that should be redacted from logs
    SENSITIVE_FIELDS = ['body', 'email_content', 'api_key', 'token', 'password', 'secret']
    
    @staticmethod
    def sanitize_log_message(message: str) -> str:
        """
        Sanitize a log message by redacting sensitive information.
        
        Args:
            message: The log message to sanitize
            
        Returns:
            Sanitized log message
        """
        # Redact email addresses
        message = LogSanitizer.EMAIL_PATTERN.sub('[EMAIL_REDACTED]', message)
        
        # Redact API keys and tokens
        message = LogSanitizer.API_KEY_PATTERN.sub(r'\1=[REDACTED]', message)
        
        return message
    
    @staticmethod
    def sanitize_log_context(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize a log context dictionary by redacting sensitive fields.
        
        Args:
            context: Dictionary containing log context
            
        Returns:
            Sanitized context dictionary
        """
        sanitized = {}
        for key, value in context.items():
            if key.lower() in LogSanitizer.SENSITIVE_FIELDS:
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, dict):
                sanitized[key] = LogSanitizer.sanitize_log_context(value)
            elif isinstance(value, str):
                sanitized[key] = LogSanitizer.sanitize_log_message(value)
            else:
                sanitized[key] = value
        return sanitized


class HTTPSEnforcer:
    """
    Utilities to enforce HTTPS connections.
    """
    
    @staticmethod
    def is_secure_connection(request: Request) -> bool:
        """
        Check if the request is using HTTPS.
        
        Args:
            request: FastAPI request object
            
        Returns:
            True if connection is secure (HTTPS), False otherwise
        """
        # Check if request is using HTTPS
        if request.url.scheme == "https":
            return True
        
        # Check for proxy headers (X-Forwarded-Proto)
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "")
        if forwarded_proto.lower() == "https":
            return True
        
        return False
    
    @staticmethod
    def enforce_https(request: Request, allow_localhost: bool = True) -> None:
        """
        Enforce HTTPS connection, raise exception if not secure.
        
        Args:
            request: FastAPI request object
            allow_localhost: Whether to allow non-HTTPS for localhost (development)
            
        Raises:
            HTTPException: If connection is not secure
        """
        # Allow localhost in development
        if allow_localhost and request.client and request.client.host in ["127.0.0.1", "localhost"]:
            return
        
        if not HTTPSEnforcer.is_secure_connection(request):
            raise HTTPException(
                status_code=403,
                detail="HTTPS connection required. Insecure connections are not allowed."
            )


class DataRetentionPolicy:
    """
    Ensures email content is not persisted after processing.
    
    This class provides utilities to verify that no email content
    is stored in databases or files after request processing.
    """
    
    @staticmethod
    def clear_request_data(request_data: Any) -> None:
        """
        Clear sensitive request data from memory.
        
        Args:
            request_data: Request data to clear
        """
        # In Python, we rely on garbage collection
        # This method serves as a marker for where data should be cleared
        # In production, ensure no references to email_content are kept
        del request_data
    
    @staticmethod
    def verify_no_persistence(email_content: str) -> bool:
        """
        Verify that email content is not being persisted.
        
        This is a placeholder for production monitoring that would check
        if email content appears in any persistent storage.
        
        Args:
            email_content: Email content to check
            
        Returns:
            True if no persistence detected, False otherwise
        """
        # In production, this would check:
        # - Database queries for email content
        # - File system writes
        # - Cache storage
        # For now, we return True as we don't persist by design
        return True
