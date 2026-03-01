# Implementation Plan: AI Execution Agent

## Overview

This implementation plan breaks down the AI Execution Agent into discrete coding tasks. The system consists of a Chrome Extension (TypeScript) frontend and a Python FastAPI backend. Tasks are organized to build incrementally, with testing integrated throughout.

## Tasks

- [x] 1. Set up project structure and development environment
  - Create backend directory structure: `backend/`, `backend/services/`, `backend/models/`, `backend/tests/`
  - Create extension directory structure: `extension/`, `extension/content/`, `extension/ui/`, `extension/api/`
  - Set up Python virtual environment and install dependencies: FastAPI, Pydantic, python-dateutil, google-api-python-client, openai/google-generativeai, hypothesis (testing)
  - Set up TypeScript configuration for Chrome Extension with Manifest V3
  - Install extension dependencies: fast-check (testing)
  - Create manifest.json with required permissions and service worker configuration
  - _Requirements: 17.1, 17.2, 17.3_

- [x] 2. Implement backend API foundation
  - [x] 2.1 Create Pydantic models for request/response
    - Implement `EmailContentModel`, `ThreadMessageModel`, `ForwardedMessageModel`
    - Implement `RunAgentRequestModel` with validation
    - Implement `TaskModel` with confidence score validation (0.0-1.0)
    - Implement `RunAgentResponseModel`, `FeedbackStatsModel`, `LogEntryModel`, `ErrorDetailModel`
    - _Requirements: 13.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_
  
  - [x] 2.2 Write property test for task validation
    - **Property 4: Task Structure Validation**
    - **Validates: Requirements 2.3, 2.4, 2.5, 2.6, 2.7, 2.8**
  
  - [x] 2.3 Create FastAPI application with /run-agent endpoint
    - Implement POST /run-agent endpoint with Pydantic validation
    - Add CORS middleware for Chrome Extension requests
    - Implement request validation error handling (422 responses)
    - _Requirements: 13.1, 13.2, 13.3, 13.7_
  
  - [x] 2.4 Write unit tests for API endpoint
    - Test valid request handling (200 response)
    - Test invalid request handling (422 response with validation errors)
    - Test CORS headers presence
    - _Requirements: 13.3, 13.4, 13.5, 13.6, 13.7_

- [x] 3. Implement LLM client abstraction
  - [x] 3.1 Create LLM client interface and implementations
    - Create abstract `LLMClient` base class with `complete()` method
    - Implement `OpenAIClient` for OpenAI API integration
    - Implement `GeminiClient` for Google Gemini API integration
    - Add configuration for API keys and model selection
    - _Requirements: 2.1_
  
  - [x] 3.2 Write unit tests for LLM clients
    - Test OpenAI client with mocked API responses
    - Test Gemini client with mocked API responses
    - Test error handling for API failures
    - _Requirements: 2.1_

- [x] 4. Implement task extraction service
  - [x] 4.1 Create TaskExtractionService with LLM integration
    - Implement `extract_tasks()` method with LLM prompt building
    - Build structured extraction prompt with multi-language support
    - Implement JSON parsing and validation of LLM responses
    - Implement retry logic (1 retry on JSON parse failure)
    - Add error handling for extraction failures
    - _Requirements: 2.1, 2.2, 2.9, 2.10, 12.1_
  
  - [x] 4.2 Write unit tests for extraction service
    - Test successful extraction with valid LLM response
    - Test retry logic with invalid JSON on first attempt
    - Test failure after max retries
    - Test multi-language prompt configuration
    - _Requirements: 2.9, 2.10, 12.1_
  
  - [x] 4.3 Write property test for language preservation
    - **Property 20: Language Preservation in Task Extraction**
    - **Validates: Requirements 12.2**

- [x] 5. Implement post-processing service   
  - [x] 5.1 Create PostProcessingService for priority and deadline handling
    - Implement `_assign_priority()` with deadline-based rules (<24h = High)
    - Implement keyword-based priority elevation (urgent keywords)
    - Implement `_resolve_deadline()` using python-dateutil for relative dates
    - Implement `process_tasks()` orchestration method
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 5.2 Write property test for deadline-based priority
    - **Property 5: Deadline-Based Priority Assignment**
    - **Validates: Requirements 3.1**
  
  - [x] 5.3 Write property test for keyword-based priority
    - **Property 6: Keyword-Based Priority Elevation**
    - **Validates: Requirements 3.2**
  
  - [x] 5.4 Write property test for deadline resolution
    - **Property 7: Relative Deadline Resolution**
    - **Validates: Requirements 3.3**
  
  - [x] 5.5 Write unit tests for edge cases
    - Test ambiguous deadline handling
    - Test extreme dates (far past, far future)
    - Test multiple urgent keywords
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 6. Checkpoint - Backend core services complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement calendar service
  - [x] 7.1 Create CalendarService with Google Calendar API integration
    - Implement Google Calendar API authentication setup
    - Implement `_get_events()` to query calendar events in time range
    - Implement `_parse_event_time()` for datetime parsing
    - _Requirements: 4.1_
  
  - [x] 7.2 Implement slot-finding algorithm
    - Implement `_find_nearest_available_slot()` with gap detection logic
    - Check gaps before first event, between events, and after last event
    - Ensure slots are 30-60 minutes duration
    - Select nearest slot to current time
    - Enforce deadline constraint (no slots after deadline)
    - _Requirements: 4.2, 4.3, 4.4, 4.5, 4.6_
  
  - [x] 7.3 Write property test for slot duration invariant
    - **Property 8: Calendar Slot Duration Invariant**
    - **Validates: Requirements 4.3, 4.4, 5.4**
  
  - [x] 7.4 Write property test for nearest slot selection
    - **Property 9: Nearest Slot Selection**
    - **Validates: Requirements 4.5**
  
  - [x] 7.5 Write property test for deadline constraint
    - **Property 10: Deadline Constraint Enforcement**
    - **Validates: Requirements 4.6, 4.8**
  
  - [x] 7.6 Implement calendar block creation
    - Implement `_create_calendar_block()` to create Google Calendar events
    - Set event title to task title
    - Set event description to include task details and source snippet
    - Set event duration within 30-60 minute range
    - Implement error handling for creation failures
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [x] 7.7 Write property test for block title preservation
    - **Property 11: Calendar Block Title Preservation**
    - **Validates: Requirements 5.2**
  
  - [x] 7.8 Write property test for block description inclusion
    - **Property 12: Calendar Block Description Inclusion**
    - **Validates: Requirements 5.3**
  
  - [x] 7.9 Implement find_slot_and_create_block orchestration
    - Combine slot finding and block creation
    - Return scheduling conflict error when no slot available
    - Return calendar block ID on success
    - _Requirements: 4.7, 5.1_
  
  - [x] 7.10 Write unit tests for calendar service
    - Test with fully booked calendar (scheduling conflict)
    - Test with empty calendar
    - Test with various event densities
    - Test Google Calendar API error handling
    - _Requirements: 4.1, 4.7, 5.5_

- [x] 8. Implement meeting prep service
  - [x] 8.1 Create MeetingPrepService with detection and generation
    - Implement `_is_meeting()` with keyword-based detection
    - Implement `_build_prep_prompt()` for LLM prep document generation
    - Implement `_parse_prep_response()` to parse LLM JSON response
    - Implement `detect_and_generate_prep()` orchestration method
    - Create `MeetingPrepDocument` Pydantic model
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  
  - [x] 8.2 Write property test for meeting detection
    - **Property 13: Meeting Detection by Keywords**
    - **Validates: Requirements 6.1**
  
  - [x] 8.3 Write property test for prep document completeness
    - **Property 14: Meeting Prep Document Completeness**
    - **Validates: Requirements 6.3, 6.4, 6.5, 6.6**
  
  - [x] 8.4 Write unit tests for meeting prep service
    - Test with various meeting keywords
    - Test with non-meeting tasks
    - Test LLM integration with mocked responses
    - _Requirements: 6.1, 6.2_

- [x] 9. Implement orchestration layer
  - [x] 9.1 Create AgentOrchestrator to coordinate all services
    - Implement `run_agent()` method with full execution flow
    - Coordinate extraction → post-processing → scheduling → meeting prep
    - Implement confidence threshold check (0.7) for manual review
    - Implement logging for each execution step
    - Implement error handling with graceful degradation
    - Calculate feedback stats (tasks extracted, blocks created, conflicts, manual review)
    - _Requirements: 7.1, 7.4, 10.2, 10.3, 10.4, 10.5, 16.1, 16.2_
  
  - [x] 9.2 Write property test for manual review threshold
    - **Property 15: Low Confidence Manual Review Threshold**
    - **Validates: Requirements 7.1**
  
  - [x] 9.3 Write property test for manual review no auto-schedule
    - **Property 16: Manual Review Tasks Not Auto-Scheduled**
    - **Validates: Requirements 7.4**
  
  - [x] 9.4 Write property test for statelessness
    - **Property 22: Request Statelessness**
    - **Validates: Requirements 14.1, 14.2**
  
  - [x] 9.5 Write property test for feedback stats accuracy
    - **Property 21: Feedback Stats Accuracy**
    - **Validates: Requirements 10.2, 10.3, 10.4, 10.5**
  
  - [x] 9.6 Write integration tests for full execution flow
    - Test end-to-end with mocked LLM and Calendar API
    - Test error handling at each stage
    - Test graceful degradation when one task fails
    - _Requirements: 16.1, 16.2_

- [x] 10. Wire backend components together
  - [x] 10.1 Connect orchestrator to /run-agent endpoint
    - Instantiate all services with dependencies
    - Wire orchestrator into FastAPI endpoint handler
    - Implement error response formatting
    - Add request/response logging
    - _Requirements: 13.4, 13.5, 13.6, 16.1, 16.2_
  
  - [x] 10.2 Write unit tests for endpoint integration
    - Test successful execution with valid request
    - Test error responses for various failure scenarios
    - Test logging output
    - _Requirements: 13.4, 13.5, 13.6_

- [x] 11. Implement security and privacy measures
  - [x] 11.1 Add input validation and sanitization
    - Implement input sanitization for all user-provided data
    - Add validation for email content size limits
    - Implement rate limiting for API endpoint
    - _Requirements: 18.4_
  
  - [x] 11.2 Implement data handling policies
    - Ensure email content is not persisted after processing
    - Implement log sanitization to exclude sensitive content
    - Add HTTPS enforcement
    - _Requirements: 18.1, 18.2, 18.3_
  
  - [x] 11.3 Write unit tests for security measures
    - Test input sanitization with malicious input
    - Test that email content is not stored
    - Test that logs don't contain sensitive data
    - _Requirements: 18.2, 18.3, 18.4_

- [x] 12. Checkpoint - Backend implementation complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Implement Chrome Extension content script
  - [x] 13.1 Create GmailDOMExtractor for email extraction
    - Implement `injectRunAgentButton()` to add button to Gmail UI
    - Implement `extractEmailContent()` to extract subject, body, sender, timestamp
    - Implement `extractThreadMessages()` for email threads
    - Implement `extractForwardedMessages()` for forwarded emails
    - Add error handling for malformed Gmail HTML
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_
  
  - [x] 13.2 Write property test for complete field extraction
    - **Property 1: Complete Email Field Extraction**
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.5**
  
  - [x] 13.3 Write property test for thread extraction
    - **Property 2: Thread Message Extraction Completeness**
    - **Validates: Requirements 1.6**
  
  - [x] 13.4 Write property test for forwarded message extraction
    - **Property 3: Forwarded Message Extraction**
    - **Validates: Requirements 1.7**
  
  - [x] 13.5 Write unit tests for DOM extraction
    - Test with various Gmail HTML structures
    - Test with empty emails
    - Test with malformed HTML
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

- [x] 14. Implement backend API client
  - [x] 14.1 Create BackendAPIClient for communication
    - Implement `runAgent()` method to POST to /run-agent
    - Add HTTPS enforcement
    - Implement error handling for network failures
    - Implement timeout handling
    - Parse and return structured response
    - _Requirements: 13.1, 18.1_
  
  - [x] 14.2 Write unit tests for API client
    - Test successful request/response
    - Test error handling for network failures
    - Test timeout handling
    - Test HTTPS enforcement
    - _Requirements: 13.1, 18.1_

- [x] 15. Implement task board UI renderer
  - [x] 15.1 Create TaskBoardRenderer for UI display
    - Implement `renderTaskBoard()` to display tasks
    - Implement `groupTasksByTimeline()` for Today/Tomorrow/Upcoming grouping
    - Implement task display with all required fields (title, description, deadline, owner, confidence, priority)
    - Add visual indicators for manual review tasks
    - Implement read-only display (no edit controls for title/description)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 8.10, 7.2, 7.3_
  
  - [x] 15.2 Write property test for timeline grouping
    - **Property 17: Timeline Grouping Correctness**
    - **Validates: Requirements 8.2**
  
  - [x] 15.3 Write property test for display completeness
    - **Property 18: Task Display Completeness**
    - **Validates: Requirements 8.3, 8.4, 8.5, 8.6, 8.7, 8.8**
  
  - [x] 15.4 Write unit tests for UI rendering
    - Test with empty task list
    - Test with tasks in all timeline groups
    - Test with manual review tasks
    - Test with scheduling conflict tasks
    - _Requirements: 8.1, 8.2, 7.2_

- [x] 16. Implement feedback panel and logging
  - [x] 16.1 Create feedback panel renderer
    - Implement `renderFeedbackPanel()` to display stats
    - Display counts: tasks extracted, calendar blocks created, scheduling conflicts, manual review items
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x] 16.2 Create execution log renderer
    - Implement `renderExecutionLog()` to display log entries
    - Display timestamps and messages for each step
    - Display warnings and errors
    - _Requirements: 16.5_
  
  - [x] 16.3 Write unit tests for feedback and logging UI
    - Test feedback panel with various stat values
    - Test log panel with various log entries
    - Test error display
    - _Requirements: 10.1, 16.5_

- [x] 17. Implement task action handlers
  - [x] 17.1 Create TaskActionHandler for user interactions
    - Implement `adjustDeadline()` with date picker integration
    - Implement `discardTask()` to remove task from display
    - Add event listeners for deadline adjustment
    - Add event listeners for discard button
    - Ensure no editing of title/description/owner
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_
  
  - [x] 17.2 Write unit tests for task actions
    - Test deadline adjustment
    - Test task discard
    - Test that title/description/owner cannot be edited
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [x] 18. Implement export functionality
  - [x] 18.1 Create CSV export for tasks
    - Implement `exportTasksToCSV()` to generate CSV file
    - Include all required fields: title, description, deadline, owner, priority, confidence
    - Add CSV export button to UI
    - Handle special characters and escaping
    - _Requirements: 11.1, 11.2, 11.3_
  
  - [x] 18.2 Write property test for CSV completeness
    - **Property 19: CSV Export Field Completeness**
    - **Validates: Requirements 11.3**
  
  - [x] 18.3 Create PDF export for meeting prep documents
    - Implement `exportMeetingPrepToPDF()` to generate PDF
    - Format prep document sections properly
    - Add PDF export button to meeting prep display
    - _Requirements: 11.4, 11.5_
  
  - [x] 18.4 Write unit tests for export functionality
    - Test CSV generation with various task data
    - Test CSV with special characters
    - Test PDF generation with meeting prep data
    - _Requirements: 11.2, 11.3, 11.5_

- [x] 19. Implement user-initiated execution controls
  - [x] 19.1 Wire "Run Agent" button to execution flow
    - Add click event listener to "Run Agent" button
    - Extract email content on button click
    - Call backend API with extracted content
    - Render results (task board, feedback, logs)
    - Display errors if execution fails
    - _Requirements: 15.5, 16.3_
  
  - [x] 19.2 Ensure no automatic execution
    - Verify no execution on page load
    - Verify no background execution
    - Verify no polling or real-time sync
    - _Requirements: 15.1, 15.2, 15.3, 15.4_
  
  - [x] 19.3 Write unit tests for execution controls
    - Test that button click triggers execution
    - Test that page load does not trigger execution
    - Test that no background execution occurs
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

- [x] 20. Implement error display in extension
  - [x] 20.1 Create error display component
    - Implement error message rendering
    - Display error code and message
    - Provide actionable guidance when available
    - Add error styling for visibility
    - _Requirements: 16.3, 16.4_
  
  - [x] 20.2 Write unit tests for error display
    - Test with various error types
    - Test error message formatting
    - _Requirements: 16.3_

- [x] 21. Wire all extension components together
  - [x] 21.1 Integrate all extension components
    - Connect DOM extractor → API client → UI renderer
    - Wire task actions to UI events
    - Wire export functionality to UI buttons
    - Ensure proper error propagation
    - _Requirements: 1.1, 8.1, 9.1, 11.1_
  
  - [x] 21.2 Write integration tests for extension
    - Test full flow: button click → extraction → API call → rendering
    - Test error handling throughout flow
    - Test task actions integration
    - _Requirements: 1.1, 8.1, 15.5_

- [x] 22. Configure Chrome Extension manifest and permissions
  - [x] 22.1 Finalize manifest.json configuration
    - Set Manifest V3 specification
    - Declare required permissions (activeTab, storage, host permissions for Gmail)
    - Configure service worker
    - Set content script injection rules for Gmail
    - Add extension metadata (name, description, version, icons)
    - _Requirements: 17.1, 17.2, 17.3, 18.5_
  
  - [x] 22.2 Write tests for manifest validation
    - Verify manifest is valid V3 format
    - Verify all required permissions are declared
    - Verify service worker configuration
    - _Requirements: 17.1, 17.2, 17.3_

- [x] 23. Final checkpoint - Full system integration
  - Ensure all tests pass, ask the user if questions arise.

- [x] 24. Create configuration and deployment documentation
  - [x] 24.1 Create backend configuration guide
    - Document environment variables (LLM API keys, Google Calendar credentials)
    - Document how to set up Google Calendar API authentication
    - Document how to run the FastAPI server
    - Document testing commands
  
  - [x] 24.2 Create extension installation guide
    - Document how to load unpacked extension in Chrome
    - Document how to configure backend API endpoint
    - Document how to test the extension
  
  - [x] 24.3 Create README with project overview
    - Document architecture overview
    - Document tech stack
    - Document core features
    - Document critical constraints
    - Link to configuration guides

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- Backend uses Python 3.10+ with FastAPI, Pydantic, hypothesis for testing
- Extension uses TypeScript with fast-check for testing
- All property tests must include comment tags: `# Feature: ai-execution-agent, Property {number}: {property_text}`
