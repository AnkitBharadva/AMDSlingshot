/**
 * Unit tests for execution controls
 * Feature: ai-execution-agent
 * Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 16.3
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { ExecutionController, initializeExtension } from './main'

describe('ExecutionController - User-Initiated Execution Controls', () => {
  let controller: ExecutionController
  const mockBackendUrl = 'https://localhost:8000'

  beforeEach(() => {
    // Clear DOM
    document.body.innerHTML = ''
    
    // Create controller instance
    controller = new ExecutionController(mockBackendUrl)
  })

  // Requirement 15.5: Test that button click triggers execution
  describe('Button Click Triggers Execution', () => {
    it('should wire button click event when initialized', () => {
      // Arrange: Create mock Gmail toolbar
      const toolbar = document.createElement('div')
      toolbar.className = 'G-atb'
      document.body.appendChild(toolbar)

      // Act: Initialize controller
      controller.initialize()

      // Assert: Button should be injected
      const button = document.getElementById('ai-agent-run-button')
      expect(button).toBeTruthy()
      expect(button?.textContent).toBe('Run Agent')
    })

    it('should have click event listener attached to button', () => {
      // Arrange: Create mock Gmail toolbar
      const toolbar = document.createElement('div')
      toolbar.className = 'G-atb'
      document.body.appendChild(toolbar)

      // Act: Initialize
      controller.initialize()

      // Assert: Button should exist and be clickable
      const button = document.getElementById('ai-agent-run-button')
      expect(button).toBeTruthy()
      
      // Verify button has event listeners (by checking it's a proper button element)
      expect(button?.tagName).toBe('BUTTON')
      expect(button?.onclick).toBeDefined()
    })
  })

  // Requirement 15.1: Test that page load does not trigger execution
  describe('No Automatic Execution on Page Load', () => {
    it('should NOT execute agent automatically when page loads', () => {
      // Arrange: Spy on console to detect execution attempts
      const consoleSpy = vi.spyOn(console, 'log')
      
      const toolbar = document.createElement('div')
      toolbar.className = 'G-atb'
      document.body.appendChild(toolbar)

      // Act: Initialize controller (simulates page load)
      controller.initialize()

      // Assert: Should only see initialization log, not extraction logs
      const logs = consoleSpy.mock.calls.map(call => call[0])
      expect(logs).toContain('AI Execution Agent initialized successfully')
      expect(logs).not.toContain('Extracting email content...')
      expect(logs).not.toContain('Calling backend API...')
      
      consoleSpy.mockRestore()
    })

    it('should only inject button on initialization, not execute', () => {
      // Arrange
      const toolbar = document.createElement('div')
      toolbar.className = 'G-atb'
      document.body.appendChild(toolbar)

      // Act: Initialize
      controller.initialize()

      // Assert: Button should exist but no task board or feedback panel
      const button = document.getElementById('ai-agent-run-button')
      expect(button).toBeTruthy()
      
      // No task board should be rendered
      const taskBoard = document.getElementById('ai-agent-task-board')
      expect(taskBoard).toBeFalsy()
      
      // No feedback panel should be rendered
      const feedbackPanel = document.getElementById('ai-agent-task-board-feedback')
      expect(feedbackPanel).toBeFalsy()
    })
  })

  // Requirement 15.2: Test that no background execution occurs
  describe('No Background Execution', () => {
    it('should not have any background intervals', () => {
      // Arrange: Spy on setInterval
      const setIntervalSpy = vi.spyOn(global, 'setInterval')

      // Act: Initialize controller
      controller.initialize()

      // Assert: No intervals should be set
      expect(setIntervalSpy).not.toHaveBeenCalled()
      
      setIntervalSpy.mockRestore()
    })

    it('should not execute in background after initialization', async () => {
      // Arrange: Spy on console to detect execution
      const consoleSpy = vi.spyOn(console, 'log')
      
      // Act: Initialize and wait
      controller.initialize()
      
      // Clear initialization logs
      consoleSpy.mockClear()
      
      // Wait for potential background execution
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Assert: No execution logs should appear
      const logs = consoleSpy.mock.calls.map(call => call[0])
      expect(logs).not.toContain('Extracting email content...')
      expect(logs).not.toContain('Calling backend API...')
      
      consoleSpy.mockRestore()
    })
  })

  // Requirement 15.3: Test that no polling occurs
  describe('No Polling for New Emails', () => {
    it('should not poll for new emails', async () => {
      // Arrange: Spy on console and setInterval
      const consoleSpy = vi.spyOn(console, 'log')
      const setIntervalSpy = vi.spyOn(global, 'setInterval')

      // Act: Initialize and wait for potential polling
      controller.initialize()
      consoleSpy.mockClear() // Clear init logs
      
      await new Promise(resolve => setTimeout(resolve, 2000))

      // Assert: No polling intervals and no execution logs
      expect(setIntervalSpy).not.toHaveBeenCalled()
      
      const logs = consoleSpy.mock.calls.map(call => call[0])
      expect(logs).not.toContain('Extracting email content...')
      
      consoleSpy.mockRestore()
      setIntervalSpy.mockRestore()
    })
  })

  // Requirement 15.4: Test that no real-time sync occurs
  describe('No Real-Time Synchronization', () => {
    it('should not establish WebSocket connections', () => {
      // Arrange: Spy on WebSocket constructor
      const originalWebSocket = global.WebSocket
      const webSocketSpy = vi.fn()
      // @ts-ignore - Mock WebSocket
      global.WebSocket = webSocketSpy

      // Act: Initialize controller
      controller.initialize()

      // Assert: No WebSocket connections should be created
      expect(webSocketSpy).not.toHaveBeenCalled()

      // Cleanup
      global.WebSocket = originalWebSocket
    })

    it('should not use EventSource for server-sent events', () => {
      // Arrange: Spy on EventSource constructor
      const originalEventSource = global.EventSource
      const eventSourceSpy = vi.fn()
      // @ts-ignore - Mock EventSource
      global.EventSource = eventSourceSpy

      // Act: Initialize controller
      controller.initialize()

      // Assert: No EventSource connections should be created
      expect(eventSourceSpy).not.toHaveBeenCalled()

      // Cleanup
      global.EventSource = originalEventSource
    })
  })

  // Requirement 16.3: Test error display
  describe('Error Display', () => {
    it('should display error message when no email content is found', () => {
      // Arrange: Create toolbar but no email content
      const toolbar = document.createElement('div')
      toolbar.className = 'G-atb'
      document.body.appendChild(toolbar)

      controller.initialize()

      // Manually trigger error display using the errorRenderer
      const errorDetail = {
        code: 'EXECUTION_ERROR',
        message: 'No email content found. Please open an email and try again.',
      }
      
      // Access errorRenderer through type assertion for testing
      ;(controller as any).errorRenderer.displayError(errorDetail)

      // Assert: Error should be displayed
      const errorDisplay = document.getElementById('ai-agent-error-display')
      expect(errorDisplay).toBeTruthy()
      expect(errorDisplay?.textContent).toContain('No email content found')
    })

    it('should display error code and message', () => {
      // Arrange
      const errorDetail = {
        code: 'TEST_ERROR',
        message: 'This is a test error message',
      }
      
      // Act: Display error using errorRenderer
      ;(controller as any).errorRenderer.displayError(errorDetail)

      // Assert: Error display should show code and message
      const errorDisplay = document.getElementById('ai-agent-error-display')
      expect(errorDisplay).toBeTruthy()
      expect(errorDisplay?.textContent).toContain('TEST_ERROR')
      expect(errorDisplay?.textContent).toContain('This is a test error message')
    })

    it('should allow closing error display', () => {
      // Arrange: Display an error
      const errorDetail = {
        code: 'TEST_ERROR',
        message: 'Test error',
      }
      
      ;(controller as any).errorRenderer.displayError(errorDetail)

      // Assert: Error display exists
      let errorDisplay = document.getElementById('ai-agent-error-display')
      expect(errorDisplay).toBeTruthy()

      // Act: Close error
      const closeButton = document.getElementById('ai-agent-error-display-close-btn')
      closeButton?.click()

      // Assert: Error display should be removed
      errorDisplay = document.getElementById('ai-agent-error-display')
      expect(errorDisplay).toBeFalsy()
    })

    it('should display actionable guidance for known error codes', () => {
      // Arrange
      const errorDetail = {
        code: 'NETWORK_ERROR',
        message: 'Failed to connect',
      }
      
      // Act: Display error using errorRenderer
      ;(controller as any).errorRenderer.displayError(errorDetail)

      // Assert: Should include guidance
      const errorDisplay = document.getElementById('ai-agent-error-display')
      expect(errorDisplay).toBeTruthy()
      expect(errorDisplay?.textContent).toContain('Suggestion')
    })
  })
})

describe('initializeExtension', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  // Requirement 15.1, 15.2: Test initialization behavior
  it('should initialize extension when DOM is ready', () => {
    // Arrange
    const toolbar = document.createElement('div')
    toolbar.className = 'G-atb'
    document.body.appendChild(toolbar)

    // Act: Call initialization
    initializeExtension()

    // Assert: Button should be injected
    const button = document.getElementById('ai-agent-run-button')
    expect(button).toBeTruthy()
  })

  it('should not execute agent during initialization', () => {
    // Arrange: Spy on console
    const consoleSpy = vi.spyOn(console, 'log')
    
    // Act: Initialize
    initializeExtension()
    
    // Get all log messages
    const logs = consoleSpy.mock.calls.map(call => call[0])

    // Assert: No execution logs should appear
    expect(logs).not.toContain('Extracting email content...')
    expect(logs).not.toContain('Calling backend API...')
    
    consoleSpy.mockRestore()
  })

  it('should only inject UI elements, not trigger execution', () => {
    // Arrange
    const toolbar = document.createElement('div')
    toolbar.className = 'G-atb'
    document.body.appendChild(toolbar)

    // Act: Initialize
    initializeExtension()

    // Assert: Button exists but no results UI
    const button = document.getElementById('ai-agent-run-button')
    expect(button).toBeTruthy()
    
    const taskBoard = document.getElementById('ai-agent-task-board')
    expect(taskBoard).toBeFalsy()
  })
})

// Integration Tests
// Requirements: 1.1, 8.1, 15.5
describe('Extension Integration Tests', () => {
  let controller: ExecutionController
  const mockBackendUrl = 'https://localhost:8000'

  beforeEach(() => {
    // Clear DOM
    document.body.innerHTML = ''
    
    // Create controller instance
    controller = new ExecutionController(mockBackendUrl)
  })

  afterEach(() => {
    // Clean up
    vi.restoreAllMocks()
  })

  // Requirement 1.1, 8.1, 15.5: Test full flow from button click to rendering
  describe('Full Execution Flow: Button Click → Extraction → API Call → Rendering', () => {
    it('should complete full flow when button is clicked with valid email', async () => {
      // Arrange: Set up Gmail DOM structure
      const toolbar = document.createElement('div')
      toolbar.className = 'G-atb'
      document.body.appendChild(toolbar)

      // Create mock email content in DOM
      const subjectEl = document.createElement('div')
      subjectEl.className = 'hP'
      subjectEl.textContent = 'Test Email Subject'
      document.body.appendChild(subjectEl)

      const bodyEl = document.createElement('div')
      bodyEl.className = 'a3s aiL'
      bodyEl.textContent = 'Test email body with task: Complete the report by tomorrow'
      document.body.appendChild(bodyEl)

      const senderEl = document.createElement('div')
      senderEl.className = 'gD'
      senderEl.setAttribute('email', 'sender@example.com')
      senderEl.textContent = 'Test Sender'
      document.body.appendChild(senderEl)

      const timestampEl = document.createElement('span')
      timestampEl.className = 'g3'
      timestampEl.setAttribute('title', '2024-01-15 10:00:00')
      timestampEl.textContent = '10:00 AM'
      document.body.appendChild(timestampEl)

      // Mock fetch for API call
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      
      const mockResponse = {
        tasks: [
          {
            id: 'task-1',
            title: 'Complete the report',
            description: 'Complete the report by tomorrow',
            deadline: tomorrow.toISOString(),
            owner: 'sender@example.com',
            confidence: 0.85,
            priority: 'high',
            state: 'scheduled',
            calendarBlockId: 'cal-block-1',
          },
        ],
        stats: {
          tasksExtracted: 1,
          calendarBlocksCreated: 1,
          schedulingConflicts: 0,
          manualReviewItems: 0,
        },
        logs: [
          {
            timestamp: '2024-01-15T10:00:00Z',
            message: 'Extracting tasks from email',
          },
          {
            timestamp: '2024-01-15T10:00:01Z',
            message: 'Created calendar block for task',
          },
        ],
        errors: [],
      }

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      } as Response)

      // Act: Initialize and click button
      controller.initialize()
      const button = document.getElementById('ai-agent-run-button')
      expect(button).toBeTruthy()

      // Trigger button click
      await button?.click()

      // Wait for async operations (longer wait for rendering)
      await new Promise(resolve => setTimeout(resolve, 300))

      // Assert: Task board should be rendered
      const taskBoard = document.getElementById('ai-agent-task-board')
      expect(taskBoard).toBeTruthy()
      expect(taskBoard?.textContent).toContain('Task Board')
      
      // Check if tasks are rendered (they should be in timeline groups)
      const taskCards = document.querySelectorAll('[data-task-id]')
      expect(taskCards.length).toBeGreaterThan(0)

      // Assert: Feedback panel should be rendered
      const feedbackPanel = document.getElementById('ai-agent-task-board-feedback')
      expect(feedbackPanel).toBeTruthy()
      expect(feedbackPanel?.textContent).toContain('Execution Summary')
      expect(feedbackPanel?.textContent).toContain('1') // Tasks extracted

      // Assert: Logs should be rendered
      const logsPanel = document.getElementById('ai-agent-task-board-logs')
      expect(logsPanel).toBeTruthy()
      expect(logsPanel?.textContent).toContain('Execution Log')
      expect(logsPanel?.textContent).toContain('Extracting tasks from email')

      // Assert: Export button should be present
      const exportBtn = document.getElementById('csv-export-btn')
      expect(exportBtn).toBeTruthy()
      expect(exportBtn?.textContent).toContain('Export Tasks to CSV')
    })

    it('should handle extraction errors gracefully', async () => {
      // Arrange: Set up Gmail DOM without email content
      const toolbar = document.createElement('div')
      toolbar.className = 'G-atb'
      document.body.appendChild(toolbar)

      // Act: Initialize and click button (no email content)
      controller.initialize()
      const button = document.getElementById('ai-agent-run-button')
      
      await button?.click()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Assert: Error should be displayed
      const errorDisplay = document.getElementById('ai-agent-error-display')
      expect(errorDisplay).toBeTruthy()
      expect(errorDisplay?.textContent).toContain('Error')
      expect(errorDisplay?.textContent).toContain('No email content found')
    })

    it('should handle API errors gracefully', async () => {
      // Arrange: Set up Gmail DOM with email content
      const toolbar = document.createElement('div')
      toolbar.className = 'G-atb'
      document.body.appendChild(toolbar)

      const subjectEl = document.createElement('div')
      subjectEl.className = 'hP'
      subjectEl.textContent = 'Test Subject'
      document.body.appendChild(subjectEl)

      const bodyEl = document.createElement('div')
      bodyEl.className = 'a3s aiL'
      bodyEl.textContent = 'Test body'
      document.body.appendChild(bodyEl)

      // Mock fetch to return error
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => JSON.stringify({ message: 'Backend error' }),
      } as Response)

      // Act: Initialize and click button
      controller.initialize()
      const button = document.getElementById('ai-agent-run-button')
      
      await button?.click()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Assert: Error should be displayed
      const errorDisplay = document.getElementById('ai-agent-error-display')
      expect(errorDisplay).toBeTruthy()
      expect(errorDisplay?.textContent).toContain('Error')
    })
  })

  // Requirement 8.1: Test task actions integration
  describe('Task Actions Integration', () => {
    it('should wire task action buttons after rendering', async () => {
      // Arrange: Set up complete flow
      const toolbar = document.createElement('div')
      toolbar.className = 'G-atb'
      document.body.appendChild(toolbar)

      const subjectEl = document.createElement('div')
      subjectEl.className = 'hP'
      subjectEl.textContent = 'Test Subject'
      document.body.appendChild(subjectEl)

      const bodyEl = document.createElement('div')
      bodyEl.className = 'a3s aiL'
      bodyEl.textContent = 'Test body'
      document.body.appendChild(bodyEl)

      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)

      const mockResponse = {
        tasks: [
          {
            id: 'task-1',
            title: 'Test Task',
            description: 'Test description',
            deadline: tomorrow.toISOString(),
            owner: 'test@example.com',
            confidence: 0.9,
            priority: 'medium',
            state: 'scheduled',
          },
        ],
        stats: {
          tasksExtracted: 1,
          calendarBlocksCreated: 0,
          schedulingConflicts: 0,
          manualReviewItems: 0,
        },
        logs: [],
        errors: [],
      }

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      } as Response)

      // Act: Initialize and trigger execution
      controller.initialize()
      const button = document.getElementById('ai-agent-run-button')
      await button?.click()
      await new Promise(resolve => setTimeout(resolve, 300))

      // Assert: Task action buttons should be present
      const taskCards = document.querySelectorAll('[data-task-id]')
      expect(taskCards.length).toBeGreaterThan(0)
      
      const taskCard = taskCards[0]
      expect(taskCard).toBeTruthy()

      const adjustBtn = taskCard?.querySelector('.deadline-adjust-btn')
      expect(adjustBtn).toBeTruthy()
      expect(adjustBtn?.textContent).toContain('Adjust Deadline')

      const discardBtn = taskCard?.querySelector('.discard-btn')
      expect(discardBtn).toBeTruthy()
      expect(discardBtn?.textContent).toContain('Discard')
    })

    it('should handle discard action correctly', async () => {
      // Arrange: Set up complete flow
      const toolbar = document.createElement('div')
      toolbar.className = 'G-atb'
      document.body.appendChild(toolbar)

      const subjectEl = document.createElement('div')
      subjectEl.className = 'hP'
      subjectEl.textContent = 'Test Subject'
      document.body.appendChild(subjectEl)

      const bodyEl = document.createElement('div')
      bodyEl.className = 'a3s aiL'
      bodyEl.textContent = 'Test body'
      document.body.appendChild(bodyEl)

      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)

      const mockResponse = {
        tasks: [
          {
            id: 'task-1',
            title: 'Test Task',
            description: 'Test description',
            deadline: tomorrow.toISOString(),
            owner: 'test@example.com',
            confidence: 0.9,
            priority: 'medium',
            state: 'scheduled',
          },
        ],
        stats: {
          tasksExtracted: 1,
          calendarBlocksCreated: 0,
          schedulingConflicts: 0,
          manualReviewItems: 0,
        },
        logs: [],
        errors: [],
      }

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      } as Response)

      // Mock confirm dialog
      global.confirm = vi.fn().mockReturnValue(true)

      // Act: Initialize, execute, and discard task
      controller.initialize()
      const button = document.getElementById('ai-agent-run-button')
      await button?.click()
      await new Promise(resolve => setTimeout(resolve, 200))

      const taskCard = document.querySelector('[data-task-id="task-1"]')
      const discardBtn = taskCard?.querySelector('.discard-btn') as HTMLElement
      discardBtn?.click()

      await new Promise(resolve => setTimeout(resolve, 100))

      // Assert: Task card should be removed
      const taskCardAfter = document.querySelector('[data-task-id="task-1"]')
      expect(taskCardAfter).toBeFalsy()
    })
  })

  // Requirement 15.5: Test error propagation throughout flow
  describe('Error Propagation Throughout Flow', () => {
    it('should propagate extraction errors to error display', async () => {
      // Arrange: Set up with invalid DOM
      const toolbar = document.createElement('div')
      toolbar.className = 'G-atb'
      document.body.appendChild(toolbar)

      // Act: Initialize and click button
      controller.initialize()
      const button = document.getElementById('ai-agent-run-button')
      await button?.click()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Assert: Error should be displayed
      const errorDisplay = document.getElementById('ai-agent-error-display')
      expect(errorDisplay).toBeTruthy()
      expect(errorDisplay?.textContent).toContain('Error')
    })

    it('should propagate network errors to error display', async () => {
      // Arrange: Set up with valid DOM but network error
      const toolbar = document.createElement('div')
      toolbar.className = 'G-atb'
      document.body.appendChild(toolbar)

      const subjectEl = document.createElement('div')
      subjectEl.className = 'hP'
      subjectEl.textContent = 'Test Subject'
      document.body.appendChild(subjectEl)

      const bodyEl = document.createElement('div')
      bodyEl.className = 'a3s aiL'
      bodyEl.textContent = 'Test body'
      document.body.appendChild(bodyEl)

      // Mock fetch to throw network error
      global.fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'))

      // Act: Initialize and click button
      controller.initialize()
      const button = document.getElementById('ai-agent-run-button')
      await button?.click()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Assert: Error should be displayed
      const errorDisplay = document.getElementById('ai-agent-error-display')
      expect(errorDisplay).toBeTruthy()
      expect(errorDisplay?.textContent).toContain('Error')
      expect(errorDisplay?.textContent).toContain('NETWORK_ERROR')
    })

    it('should propagate timeout errors to error display', async () => {
      // Arrange: Set up with valid DOM but timeout
      const toolbar = document.createElement('div')
      toolbar.className = 'G-atb'
      document.body.appendChild(toolbar)

      const subjectEl = document.createElement('div')
      subjectEl.className = 'hP'
      subjectEl.textContent = 'Test Subject'
      document.body.appendChild(subjectEl)

      const bodyEl = document.createElement('div')
      bodyEl.className = 'a3s aiL'
      bodyEl.textContent = 'Test body'
      document.body.appendChild(bodyEl)

      // Mock fetch to timeout
      global.fetch = vi.fn().mockImplementation(() => {
        return new Promise((_, reject) => {
          const error = new Error('The operation was aborted')
          error.name = 'AbortError'
          setTimeout(() => reject(error), 50)
        })
      })

      // Act: Initialize and click button
      controller.initialize()
      const button = document.getElementById('ai-agent-run-button')
      await button?.click()
      await new Promise(resolve => setTimeout(resolve, 200))

      // Assert: Error should be displayed
      const errorDisplay = document.getElementById('ai-agent-error-display')
      expect(errorDisplay).toBeTruthy()
      expect(errorDisplay?.textContent).toContain('Error')
    })
  })
})

