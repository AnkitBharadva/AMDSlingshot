"""Test script to debug service initialization."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Environment variables loaded:")
print(f"LLM_PROVIDER: {os.environ.get('LLM_PROVIDER')}")
print(f"OPENAI_API_KEY: {'Set' if os.environ.get('OPENAI_API_KEY') else 'Not set'}")
print(f"OPENAI_MODEL: {os.environ.get('OPENAI_MODEL')}")
print()

try:
    print("Attempting to initialize OpenAI client...")
    from src.services.llm_client import OpenAIClient
    client = OpenAIClient()
    print(f"✓ OpenAI client initialized successfully with model: {client.model}")
except Exception as e:
    print(f"✗ OpenAI client initialization failed: {e}")
    import traceback
    traceback.print_exc()

print()

try:
    print("Attempting to initialize Calendar service...")
    from src.services.calendar import CalendarService
    calendar_service = CalendarService()
    print("✓ Calendar service initialized successfully")
except Exception as e:
    print(f"✗ Calendar service initialization failed: {e}")
    import traceback
    traceback.print_exc()

print()

try:
    print("Attempting to initialize all services...")
    from src.services.llm_client import OpenAIClient
    from src.services.extraction import TaskExtractionService
    from src.services.post_processing import PostProcessingService
    from src.services.calendar import CalendarService
    from src.services.meeting_prep import MeetingPrepService
    from src.services.orchestrator import AgentOrchestrator
    
    llm_client = OpenAIClient()
    extraction_service = TaskExtractionService(llm_client=llm_client)
    post_processing_service = PostProcessingService()
    calendar_service = CalendarService()
    meeting_prep_service = MeetingPrepService(llm_client=llm_client)
    
    orchestrator = AgentOrchestrator(
        extraction_service=extraction_service,
        post_processing_service=post_processing_service,
        calendar_service=calendar_service,
        meeting_prep_service=meeting_prep_service
    )
    
    print("✓ All services initialized successfully!")
    
except Exception as e:
    print(f"✗ Service initialization failed: {e}")
    import traceback
    traceback.print_exc()
