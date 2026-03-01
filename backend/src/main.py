"""
FastAPI application for the AI Execution Agent backend.

This module sets up the FastAPI server with the /run-agent endpoint
and CORS middleware for Chrome Extension requests.
"""

import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from models.models import (
    RunAgentRequestModel,
    RunAgentResponseModel,
    ErrorDetailModel,
    LogEntryModel
)
from src.services.orchestrator import AgentOrchestrator
from src.services.extraction import TaskExtractionService
from src.services.post_processing import PostProcessingService
from src.services.calendar import CalendarService
from src.services.meeting_prep import MeetingPrepService
from src.services.llm_client import OpenAIClient, GeminiClient
from src.security import InputSanitizer, RateLimiter, RateLimitMiddleware, HTTPSEnforcer, LogSanitizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Execution Agent API",
    description="Backend API for extracting tasks from emails and scheduling them",
    version="1.0.0"
)

# Configure CORS middleware for Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
rate_limiter = RateLimiter()
app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)


def _initialize_services() -> AgentOrchestrator:
    """
    Initialize all services with their dependencies.
    
    Returns:
        AgentOrchestrator: Configured orchestrator with all services.
    """
    # Determine which LLM client to use based on environment
    llm_provider = os.environ.get('LLM_PROVIDER', 'openai').lower()
    
    if llm_provider == 'gemini':
        llm_client = GeminiClient()
        logger.info("Initialized Gemini LLM client")
    else:
        llm_client = OpenAIClient()
        logger.info("Initialized OpenAI LLM client")
    
    # Load Google Calendar credentials
    from google.oauth2.credentials import Credentials
    creds = Credentials.from_authorized_user_file('token.json')
    
    # Initialize services
    extraction_service = TaskExtractionService(llm_client=llm_client)
    post_processing_service = PostProcessingService()
    calendar_service = CalendarService(credentials=creds)
    meeting_prep_service = MeetingPrepService(llm_client=llm_client)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator(
        extraction_service=extraction_service,
        post_processing_service=post_processing_service,
        calendar_service=calendar_service,
        meeting_prep_service=meeting_prep_service
    )
    
    logger.info("All services initialized successfully")
    return orchestrator


# Initialize orchestrator at startup
try:
    orchestrator = _initialize_services()
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    orchestrator = None


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors and return 422 response.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation failed",
            "errors": errors
        }
    )


@app.post(
    "/run-agent",
    response_model=RunAgentResponseModel,
    status_code=200,
    responses={
        422: {
            "description": "Validation error in request body",
            "content": {
                "application/json": {
                    "example": {"detail": "Validation failed", "errors": []}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error", "errors": []}
                }
            }
        }
    }
)
async def run_agent(request: RunAgentRequestModel):
    """
    Process email content and extract tasks.
    
    This endpoint receives email content from the Chrome Extension,
    extracts actionable tasks using LLM, schedules them on Google Calendar,
    and generates meeting preparation documents.
    
    - **request**: RunAgentRequestModel containing email content and user settings
    - **returns**: RunAgentResponseModel with extracted tasks, stats, and logs
    """
    # Enforce HTTPS (allow localhost for development)
    from fastapi import Request as FastAPIRequest
    # Note: In production, set allow_localhost=False
    # HTTPSEnforcer.enforce_https(request, allow_localhost=True)
    
    # Sanitize input data
    try:
        sanitized_email = InputSanitizer.sanitize_email_content(
            request.email_content.model_dump()
        )
        # Update request with sanitized data
        request.email_content.subject = sanitized_email.get('subject', request.email_content.subject)
        request.email_content.body = sanitized_email.get('body', request.email_content.body)
        request.email_content.sender = sanitized_email.get('sender', request.email_content.sender)
        request.email_content.timestamp = sanitized_email.get('timestamp', request.email_content.timestamp)
    except ValueError as e:
        logger.warning(f"Input validation failed: {str(e)}")
        return RunAgentResponseModel(
            tasks=[],
            stats={
                "tasks_extracted": 0,
                "calendar_blocks_created": 0,
                "scheduling_conflicts": 0,
                "manual_review_items": 0
            },
            logs=[
                LogEntryModel(
                    timestamp=datetime.now(),
                    message=f"Input validation failed: {str(e)}",
                    level="ERROR"
                )
            ],
            errors=[
                ErrorDetailModel(
                    code="INPUT_VALIDATION_ERROR",
                    message=str(e),
                    context={"step": "input_sanitization"}
                )
            ]
        )
    
    # Log incoming request (sanitized)
    sanitized_subject = LogSanitizer.sanitize_log_message(request.email_content.subject)
    logger.info(f"Received /run-agent request from user_timezone={request.user_timezone}, calendar_id={request.calendar_id}")
    logger.info(f"Email subject: {sanitized_subject}")
    
    # Check if orchestrator is initialized
    if orchestrator is None:
        logger.error("Orchestrator not initialized - services failed to start")
        return RunAgentResponseModel(
            tasks=[],
            stats={
                "tasks_extracted": 0,
                "calendar_blocks_created": 0,
                "scheduling_conflicts": 0,
                "manual_review_items": 0
            },
            logs=[
                LogEntryModel(
                    timestamp=datetime.now(),
                    message="Service initialization failed",
                    level="ERROR"
                )
            ],
            errors=[
                ErrorDetailModel(
                    code="SERVICE_INITIALIZATION_ERROR",
                    message="Backend services failed to initialize. Check API keys and configuration.",
                    context={"step": "initialization"}
                )
            ]
        )
    
    try:
        # Execute agent orchestration
        logger.info("Starting agent orchestration")
        response = orchestrator.run_agent(request)
        
        # Log response summary (no sensitive data)
        logger.info(f"Agent execution completed: {response.stats.tasks_extracted} tasks extracted, "
                   f"{response.stats.calendar_blocks_created} blocks created, "
                   f"{response.stats.scheduling_conflicts} conflicts, "
                   f"{response.stats.manual_review_items} manual review items")
        
        if response.errors:
            logger.warning(f"Agent execution completed with {len(response.errors)} errors")
            for error in response.errors:
                # Sanitize error messages before logging
                sanitized_message = LogSanitizer.sanitize_log_message(error.message)
                logger.warning(f"Error {error.code}: {sanitized_message}")
        
        # Note: Email content is not persisted - it exists only in memory during request processing
        # Python's garbage collector will clean up after response is returned
        
        return response
        
    except Exception as e:
        # Handle unexpected errors (sanitize error message)
        sanitized_error = LogSanitizer.sanitize_log_message(str(e))
        logger.error(f"Unexpected error during agent execution: {sanitized_error}", exc_info=False)
        
        return RunAgentResponseModel(
            tasks=[],
            stats={
                "tasks_extracted": 0,
                "calendar_blocks_created": 0,
                "scheduling_conflicts": 0,
                "manual_review_items": 0
            },
            logs=[
                LogEntryModel(
                    timestamp=datetime.now(),
                    message=f"Unexpected error occurred",
                    level="ERROR"
                )
            ],
            errors=[
                ErrorDetailModel(
                    code="UNEXPECTED_ERROR",
                    message="An unexpected error occurred during processing",
                    context={"step": "endpoint_handler"}
                )
            ]
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint for the API.
    """
    return {"status": "healthy"}
