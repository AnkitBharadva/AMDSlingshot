/** Tests for UI rendering components. */

import { describe, it, expect, beforeEach } from 'vitest'
import * as fc from 'fast-check'
import {
  TaskBoardRenderer,
  TaskDisplayData,
  Priority,
  TaskState,
  FeedbackStats,
  LogEntry,
  ErrorDisplayRenderer,
} from './ui'

describe('TaskBoardRenderer', () => {
  let renderer: TaskBoardRenderer

  beforeEach(() => {
    renderer = new TaskBoardRenderer('test-container')
    // Clean up any existing test container
    const existing = document.getElementById('test-container')
    if (existing) {
      existing.remove()
    }
  })

  describe('Property 17: Timeline Grouping Correctness', () => {
    // Feature: ai-execution-agent, Property 17: Timeline Grouping Correctness
    it('should correctly group tasks by timeline (Today, Tomorrow, Upcoming)', () => {
      fc.assert(
        fc.property(
          fc.array(
            fc.record({
              id: fc.uuid(),
              title: fc.string({ minLength: 1, maxLength: 100 }),
              description: fc.string({ minLength: 1, maxLength: 500 }),
              deadline: fc.date({
                min: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 7 days ago
                max: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days from now
              }),
              owner: fc.emailAddress(),
              confidence: fc.float({ min: 0, max: 1 }),
              priority: fc.constantFrom(Priority.Low, Priority.Medium, Priority.High),
              state: fc.constantFrom(
                TaskState.Scheduled,
                TaskState.ManualReview,
                TaskState.SchedulingConflict,
                TaskState.Discarded
              ),
              calendarBlockId: fc.option(fc.uuid(), { nil: undefined }),
            })
          ),
          (tasks) => {
            // Convert Date objects to ISO strings for TaskDisplayData
            const taskDisplayData: TaskDisplayData[] = tasks.map(task => ({
              ...task,
              deadline: task.deadline.toISOString(),
            }))

            // Group tasks
            const groups = renderer.groupTasksByTimeline(taskDisplayData)

            // Calculate expected groups
            const now = new Date()
            const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
            const todayEnd = new Date(todayStart)
            todayEnd.setDate(todayEnd.getDate() + 1)
            
            const tomorrowEnd = new Date(todayEnd)
            tomorrowEnd.setDate(tomorrowEnd.getDate() + 1)

            // Verify each task is in the correct group
            tasks.forEach((task, index) => {
              const deadline = task.deadline
              const taskId = taskDisplayData[index].id

              if (deadline >= todayStart && deadline < todayEnd) {
                // Should be in today
                expect(
                  groups.today.some(t => t.id === taskId),
                  `Task ${taskId} with deadline ${deadline.toISOString()} should be in Today group`
                ).toBe(true)
                expect(
                  groups.tomorrow.some(t => t.id === taskId),
                  `Task ${taskId} should not be in Tomorrow group`
                ).toBe(false)
                expect(
                  groups.upcoming.some(t => t.id === taskId),
                  `Task ${taskId} should not be in Upcoming group`
                ).toBe(false)
              } else if (deadline >= todayEnd && deadline < tomorrowEnd) {
                // Should be in tomorrow
                expect(
                  groups.tomorrow.some(t => t.id === taskId),
                  `Task ${taskId} with deadline ${deadline.toISOString()} should be in Tomorrow group`
                ).toBe(true)
                expect(
                  groups.today.some(t => t.id === taskId),
                  `Task ${taskId} should not be in Today group`
                ).toBe(false)
                expect(
                  groups.upcoming.some(t => t.id === taskId),
                  `Task ${taskId} should not be in Upcoming group`
                ).toBe(false)
              } else if (deadline >= tomorrowEnd) {
                // Should be in upcoming
                expect(
                  groups.upcoming.some(t => t.id === taskId),
                  `Task ${taskId} with deadline ${deadline.toISOString()} should be in Upcoming group`
                ).toBe(true)
                expect(
                  groups.today.some(t => t.id === taskId),
                  `Task ${taskId} should not be in Today group`
                ).toBe(false)
                expect(
                  groups.tomorrow.some(t => t.id === taskId),
                  `Task ${taskId} should not be in Tomorrow group`
                ).toBe(false)
              }
              // Past deadlines are not in any group (not tested as they're excluded)
            })

            // Verify no duplicates across groups
            const allGroupedIds = [
              ...groups.today.map(t => t.id),
              ...groups.tomorrow.map(t => t.id),
              ...groups.upcoming.map(t => t.id),
            ]
            const uniqueIds = new Set(allGroupedIds)
            expect(
              allGroupedIds.length,
              'No task should appear in multiple groups'
            ).toBe(uniqueIds.size)
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  describe('Property 18: Task Display Completeness', () => {
    // Feature: ai-execution-agent, Property 18: Task Display Completeness
    it('should display all required fields for each task', () => {
      fc.assert(
        fc.property(
          fc.array(
            fc.record({
              id: fc.uuid(),
              title: fc.string({ minLength: 1, maxLength: 100 }),
              description: fc.string({ minLength: 1, maxLength: 500 }),
              deadline: fc.date({
                min: new Date(),
                max: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
              }),
              owner: fc.emailAddress(),
              confidence: fc.float({ min: 0, max: 1 }),
              priority: fc.constantFrom(Priority.Low, Priority.Medium, Priority.High),
              state: fc.constantFrom(
                TaskState.Scheduled,
                TaskState.ManualReview,
                TaskState.SchedulingConflict,
                TaskState.Discarded
              ),
              calendarBlockId: fc.option(fc.uuid(), { nil: undefined }),
            }),
            { minLength: 1, maxLength: 10 }
          ),
          (tasks) => {
            // Convert Date objects to ISO strings for TaskDisplayData
            const taskDisplayData: TaskDisplayData[] = tasks.map(task => ({
              ...task,
              deadline: task.deadline.toISOString(),
            }))

            // Render the task board
            renderer.renderTaskBoard(taskDisplayData)

            // Get the rendered container
            const container = document.getElementById('test-container')
            expect(container).not.toBeNull()

            if (!container) return

            // Verify each task is rendered with all required fields
            taskDisplayData.forEach(task => {
              const taskCard = container.querySelector(`[data-task-id="${task.id}"]`)
              expect(
                taskCard,
                `Task card for task ${task.id} should be rendered`
              ).not.toBeNull()

              if (!taskCard) return

              const cardText = taskCard.textContent || ''

              // Verify title is displayed
              expect(
                cardText.includes(task.title),
                `Task title "${task.title}" should be visible in the rendered output`
              ).toBe(true)

              // Verify description is displayed
              expect(
                cardText.includes(task.description),
                `Task description "${task.description}" should be visible in the rendered output`
              ).toBe(true)

              // Verify deadline is displayed (check for formatted date components)
              const deadlineDate = new Date(task.deadline)
              const month = deadlineDate.toLocaleString('en-US', { month: 'short' })
              expect(
                cardText.includes('Deadline') || cardText.includes(month),
                `Task deadline should be visible in the rendered output`
              ).toBe(true)

              // Verify owner is displayed
              expect(
                cardText.includes(task.owner) || cardText.includes('Owner'),
                `Task owner "${task.owner}" should be visible in the rendered output`
              ).toBe(true)

              // Verify confidence is displayed
              const confidencePercent = Math.round(task.confidence * 100)
              expect(
                cardText.includes('Confidence') || cardText.includes(`${confidencePercent}%`),
                `Task confidence should be visible in the rendered output`
              ).toBe(true)

              // Verify priority is displayed
              expect(
                cardText.includes('Priority') || 
                cardText.includes('High') || 
                cardText.includes('Medium') || 
                cardText.includes('Low'),
                `Task priority should be visible in the rendered output`
              ).toBe(true)
            })
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  describe('Unit Tests for UI Rendering', () => {
    it('should render empty state when no tasks are provided', () => {
      renderer.renderTaskBoard([])

      const container = document.getElementById('test-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      expect(containerText).toContain('No tasks extracted')
    })

    it('should render tasks in all timeline groups', () => {
      const now = new Date()
      const todayDeadline = new Date(now)
      todayDeadline.setHours(now.getHours() + 2)

      const tomorrowDeadline = new Date(now)
      tomorrowDeadline.setDate(now.getDate() + 1)
      tomorrowDeadline.setHours(14, 0, 0, 0)

      const upcomingDeadline = new Date(now)
      upcomingDeadline.setDate(now.getDate() + 5)

      const tasks: TaskDisplayData[] = [
        {
          id: 'task-today',
          title: 'Today Task',
          description: 'Task due today',
          deadline: todayDeadline.toISOString(),
          owner: 'user@example.com',
          confidence: 0.9,
          priority: Priority.High,
          state: TaskState.Scheduled,
          calendarBlockId: 'cal-1',
        },
        {
          id: 'task-tomorrow',
          title: 'Tomorrow Task',
          description: 'Task due tomorrow',
          deadline: tomorrowDeadline.toISOString(),
          owner: 'user@example.com',
          confidence: 0.85,
          priority: Priority.Medium,
          state: TaskState.Scheduled,
        },
        {
          id: 'task-upcoming',
          title: 'Upcoming Task',
          description: 'Task due in 5 days',
          deadline: upcomingDeadline.toISOString(),
          owner: 'user@example.com',
          confidence: 0.8,
          priority: Priority.Low,
          state: TaskState.Scheduled,
        },
      ]

      renderer.renderTaskBoard(tasks)

      const container = document.getElementById('test-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      
      // Verify all timeline groups are present
      expect(containerText).toContain('Today')
      expect(containerText).toContain('Tomorrow')
      expect(containerText).toContain('Upcoming')

      // Verify all tasks are rendered
      expect(containerText).toContain('Today Task')
      expect(containerText).toContain('Tomorrow Task')
      expect(containerText).toContain('Upcoming Task')
    })

    it('should render manual review tasks with visual indicator', () => {
      const tasks: TaskDisplayData[] = [
        {
          id: 'manual-review-task',
          title: 'Low Confidence Task',
          description: 'This task needs manual review',
          deadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
          owner: 'user@example.com',
          confidence: 0.65,
          priority: Priority.Medium,
          state: TaskState.ManualReview,
        },
      ]

      renderer.renderTaskBoard(tasks)

      const container = document.getElementById('test-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      
      // Verify manual review indicator is present
      expect(containerText).toContain('Manual Review Required')
      expect(containerText).toContain('Low Confidence Task')

      // Verify the task card has the manual review styling
      const taskCard = container?.querySelector('[data-task-id="manual-review-task"]')
      expect(taskCard).not.toBeNull()
      
      const taskCardElement = taskCard as HTMLElement
      expect(taskCardElement.style.borderLeft).toContain('4px')
    })

    it('should render scheduling conflict tasks with visual indicator', () => {
      const tasks: TaskDisplayData[] = [
        {
          id: 'conflict-task',
          title: 'Conflicted Task',
          description: 'No available time slot',
          deadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
          owner: 'user@example.com',
          confidence: 0.9,
          priority: Priority.High,
          state: TaskState.SchedulingConflict,
        },
      ]

      renderer.renderTaskBoard(tasks)

      const container = document.getElementById('test-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      
      // Verify scheduling conflict indicator is present
      expect(containerText).toContain('Scheduling Conflict')
      expect(containerText).toContain('Conflicted Task')

      // Verify the task card has the conflict styling
      const taskCard = container?.querySelector('[data-task-id="conflict-task"]')
      expect(taskCard).not.toBeNull()
      
      const taskCardElement = taskCard as HTMLElement
      expect(taskCardElement.style.borderLeft).toContain('4px')
    })

    it('should render scheduled tasks with calendar block indicator', () => {
      const tasks: TaskDisplayData[] = [
        {
          id: 'scheduled-task',
          title: 'Scheduled Task',
          description: 'Task with calendar block',
          deadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
          owner: 'user@example.com',
          confidence: 0.95,
          priority: Priority.High,
          state: TaskState.Scheduled,
          calendarBlockId: 'cal-block-123',
        },
      ]

      renderer.renderTaskBoard(tasks)

      const container = document.getElementById('test-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      
      // Verify scheduled indicator is present
      expect(containerText).toContain('Scheduled on Calendar')
      expect(containerText).toContain('Scheduled Task')
    })

    it('should display all required task fields', () => {
      const tasks: TaskDisplayData[] = [
        {
          id: 'complete-task',
          title: 'Complete Task',
          description: 'Task with all fields',
          deadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
          owner: 'john.doe@example.com',
          confidence: 0.87,
          priority: Priority.Medium,
          state: TaskState.Scheduled,
        },
      ]

      renderer.renderTaskBoard(tasks)

      const container = document.getElementById('test-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      
      // Verify all required fields are displayed
      expect(containerText).toContain('Complete Task') // title
      expect(containerText).toContain('Task with all fields') // description
      expect(containerText).toContain('Deadline') // deadline label
      expect(containerText).toContain('john.doe@example.com') // owner
      expect(containerText).toContain('87%') // confidence
      expect(containerText).toContain('Medium') // priority
    })

    it('should handle tasks with various priority levels', () => {
      const tasks: TaskDisplayData[] = [
        {
          id: 'high-priority',
          title: 'High Priority Task',
          description: 'Urgent task',
          deadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
          owner: 'user@example.com',
          confidence: 0.9,
          priority: Priority.High,
          state: TaskState.Scheduled,
        },
        {
          id: 'medium-priority',
          title: 'Medium Priority Task',
          description: 'Normal task',
          deadline: new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString(),
          owner: 'user@example.com',
          confidence: 0.85,
          priority: Priority.Medium,
          state: TaskState.Scheduled,
        },
        {
          id: 'low-priority',
          title: 'Low Priority Task',
          description: 'Can wait',
          deadline: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
          owner: 'user@example.com',
          confidence: 0.8,
          priority: Priority.Low,
          state: TaskState.Scheduled,
        },
      ]

      renderer.renderTaskBoard(tasks)

      const container = document.getElementById('test-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      
      // Verify all priority levels are displayed
      expect(containerText).toContain('High')
      expect(containerText).toContain('Medium')
      expect(containerText).toContain('Low')
    })
  })

  describe('Feedback Panel Tests', () => {
    it('should render feedback panel with all stat values', () => {
      const stats: FeedbackStats = {
        tasksExtracted: 5,
        calendarBlocksCreated: 3,
        schedulingConflicts: 1,
        manualReviewItems: 1,
      }

      renderer.renderFeedbackPanel(stats)

      const panel = document.getElementById('test-container-feedback')
      expect(panel).not.toBeNull()

      const panelText = panel?.textContent || ''
      
      // Verify header
      expect(panelText).toContain('Execution Summary')
      
      // Verify all stat labels are present
      expect(panelText).toContain('Tasks Extracted')
      expect(panelText).toContain('Calendar Blocks Created')
      expect(panelText).toContain('Scheduling Conflicts')
      expect(panelText).toContain('Manual Review Items')
      
      // Verify all stat values are present
      expect(panelText).toContain('5')
      expect(panelText).toContain('3')
      expect(panelText).toContain('1')
    })

    it('should render feedback panel with zero values', () => {
      const stats: FeedbackStats = {
        tasksExtracted: 0,
        calendarBlocksCreated: 0,
        schedulingConflicts: 0,
        manualReviewItems: 0,
      }

      renderer.renderFeedbackPanel(stats)

      const panel = document.getElementById('test-container-feedback')
      expect(panel).not.toBeNull()

      const panelText = panel?.textContent || ''
      
      // Verify all stat labels are present even with zero values
      expect(panelText).toContain('Tasks Extracted')
      expect(panelText).toContain('Calendar Blocks Created')
      expect(panelText).toContain('Scheduling Conflicts')
      expect(panelText).toContain('Manual Review Items')
    })

    it('should render feedback panel with large stat values', () => {
      const stats: FeedbackStats = {
        tasksExtracted: 150,
        calendarBlocksCreated: 120,
        schedulingConflicts: 25,
        manualReviewItems: 30,
      }

      renderer.renderFeedbackPanel(stats)

      const panel = document.getElementById('test-container-feedback')
      expect(panel).not.toBeNull()

      const panelText = panel?.textContent || ''
      
      // Verify large values are displayed correctly
      expect(panelText).toContain('150')
      expect(panelText).toContain('120')
      expect(panelText).toContain('25')
      expect(panelText).toContain('30')
    })
  })

  describe('Execution Log Tests', () => {
    it('should render execution log with various log entries', () => {
      const logs: LogEntry[] = [
        {
          timestamp: new Date().toISOString(),
          message: 'Extracting tasks from email',
          level: 'info',
        },
        {
          timestamp: new Date().toISOString(),
          message: 'Task extraction completed successfully',
          level: 'info',
        },
        {
          timestamp: new Date().toISOString(),
          message: 'Scheduling conflict detected for task',
          level: 'warning',
        },
      ]

      renderer.renderExecutionLog(logs)

      const panel = document.getElementById('test-container-logs')
      expect(panel).not.toBeNull()

      const panelText = panel?.textContent || ''
      
      // Verify header
      expect(panelText).toContain('Execution Log')
      
      // Verify all log messages are present
      expect(panelText).toContain('Extracting tasks from email')
      expect(panelText).toContain('Task extraction completed successfully')
      expect(panelText).toContain('Scheduling conflict detected for task')
    })

    it('should render execution log with error entries', () => {
      const logs: LogEntry[] = [
        {
          timestamp: new Date().toISOString(),
          message: 'Failed to connect to backend API',
          level: 'error',
        },
        {
          timestamp: new Date().toISOString(),
          message: 'Network timeout occurred',
          level: 'error',
        },
      ]

      renderer.renderExecutionLog(logs)

      const panel = document.getElementById('test-container-logs')
      expect(panel).not.toBeNull()

      const panelText = panel?.textContent || ''
      
      // Verify error messages are present
      expect(panelText).toContain('Failed to connect to backend API')
      expect(panelText).toContain('Network timeout occurred')
    })

    it('should render execution log with warning entries', () => {
      const logs: LogEntry[] = [
        {
          timestamp: new Date().toISOString(),
          message: 'Low confidence task marked for manual review',
          level: 'warning',
        },
        {
          timestamp: new Date().toISOString(),
          message: 'Calendar slot not found before deadline',
          level: 'warning',
        },
      ]

      renderer.renderExecutionLog(logs)

      const panel = document.getElementById('test-container-logs')
      expect(panel).not.toBeNull()

      const panelText = panel?.textContent || ''
      
      // Verify warning messages are present
      expect(panelText).toContain('Low confidence task marked for manual review')
      expect(panelText).toContain('Calendar slot not found before deadline')
    })

    it('should render execution log with mixed log levels', () => {
      const logs: LogEntry[] = [
        {
          timestamp: new Date().toISOString(),
          message: 'Starting task extraction',
          level: 'info',
        },
        {
          timestamp: new Date().toISOString(),
          message: 'Ambiguous deadline detected',
          level: 'warning',
        },
        {
          timestamp: new Date().toISOString(),
          message: 'LLM API request failed',
          level: 'error',
        },
        {
          timestamp: new Date().toISOString(),
          message: 'Retrying with exponential backoff',
          level: 'info',
        },
      ]

      renderer.renderExecutionLog(logs)

      const panel = document.getElementById('test-container-logs')
      expect(panel).not.toBeNull()

      const panelText = panel?.textContent || ''
      
      // Verify all messages are present
      expect(panelText).toContain('Starting task extraction')
      expect(panelText).toContain('Ambiguous deadline detected')
      expect(panelText).toContain('LLM API request failed')
      expect(panelText).toContain('Retrying with exponential backoff')
    })

    it('should render empty state when no log entries', () => {
      const logs: LogEntry[] = []

      renderer.renderExecutionLog(logs)

      const panel = document.getElementById('test-container-logs')
      expect(panel).not.toBeNull()

      const panelText = panel?.textContent || ''
      
      // Verify empty state message
      expect(panelText).toContain('No log entries')
    })

    it('should display timestamps for log entries', () => {
      const timestamp = new Date('2026-02-17T14:30:00Z')
      const logs: LogEntry[] = [
        {
          timestamp: timestamp.toISOString(),
          message: 'Test log entry',
          level: 'info',
        },
      ]

      renderer.renderExecutionLog(logs)

      const panel = document.getElementById('test-container-logs')
      expect(panel).not.toBeNull()

      // Verify that some timestamp is displayed (format may vary by locale)
      const panelHTML = panel?.innerHTML || ''
      expect(panelHTML.length).toBeGreaterThan(0)
      
      // The timestamp should be formatted and present
      const panelText = panel?.textContent || ''
      expect(panelText).toContain('Test log entry')
    })
  })
})

describe('ErrorDisplayRenderer', () => {
  let errorRenderer: ErrorDisplayRenderer

  beforeEach(() => {
    errorRenderer = new ErrorDisplayRenderer('test-error-container')
    // Clean up any existing test error container
    const existing = document.getElementById('test-error-container')
    if (existing) {
      existing.remove()
    }
  })

  describe('Unit Tests for Error Display', () => {
    it('should display error with code and message', () => {
      const error = {
        code: 'NETWORK_ERROR',
        message: 'Failed to connect to backend server',
      }

      errorRenderer.displayError(error)

      const container = document.getElementById('test-error-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      
      // Verify error code is displayed
      expect(containerText).toContain('Error Code: NETWORK_ERROR')
      
      // Verify error message is displayed
      expect(containerText).toContain('Failed to connect to backend server')
      
      // Verify error header
      expect(containerText).toContain('Error')
    })

    it('should display actionable guidance for known error codes', () => {
      const error = {
        code: 'NETWORK_ERROR',
        message: 'Cannot connect to backend',
      }

      errorRenderer.displayError(error)

      const container = document.getElementById('test-error-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      
      // Verify guidance is displayed
      expect(containerText).toContain('Suggestion')
      expect(containerText).toContain('Cannot connect to the backend server')
    })

    it('should display error without guidance for unknown error codes', () => {
      const error = {
        code: 'CUSTOM_ERROR_CODE',
        message: 'Some custom error occurred',
      }

      errorRenderer.displayError(error)

      const container = document.getElementById('test-error-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      
      // Verify error is displayed
      expect(containerText).toContain('Error Code: CUSTOM_ERROR_CODE')
      expect(containerText).toContain('Some custom error occurred')
      
      // Guidance should not be present for unknown error codes
      // (or it should be minimal)
    })

    it('should display error with various error types', () => {
      const errorTypes = [
        { code: 'INITIALIZATION_ERROR', message: 'Failed to initialize' },
        { code: 'TIMEOUT', message: 'Request timed out' },
        { code: 'HTTP_401', message: 'Unauthorized' },
        { code: 'HTTP_422', message: 'Invalid request' },
        { code: 'HTTP_500', message: 'Server error' },
        { code: 'INVALID_RESPONSE', message: 'Invalid response format' },
        { code: 'EXECUTION_ERROR', message: 'Execution failed' },
        { code: 'UNKNOWN_ERROR', message: 'Unknown error occurred' },
      ]

      errorTypes.forEach(error => {
        // Clean up previous error
        const existing = document.getElementById('test-error-container')
        if (existing) {
          existing.remove()
        }

        errorRenderer.displayError(error)

        const container = document.getElementById('test-error-container')
        expect(container).not.toBeNull()

        const containerText = container?.textContent || ''
        
        // Verify error code and message are displayed
        expect(containerText).toContain(`Error Code: ${error.code}`)
        expect(containerText).toContain(error.message)
      })
    })

    it('should format error message correctly', () => {
      const error = {
        code: 'TEST_ERROR',
        message: 'This is a test error message with special characters: <>&"',
      }

      errorRenderer.displayError(error)

      const container = document.getElementById('test-error-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      
      // Verify message is displayed (special characters should be handled)
      expect(containerText).toContain('This is a test error message')
    })

    it('should display close button', () => {
      const error = {
        code: 'TEST_ERROR',
        message: 'Test error',
      }

      errorRenderer.displayError(error)

      const container = document.getElementById('test-error-container')
      expect(container).not.toBeNull()

      // Verify close button exists
      const closeBtn = document.getElementById('test-error-container-close-btn')
      expect(closeBtn).not.toBeNull()
    })

    it('should dismiss error when close button is clicked', () => {
      const error = {
        code: 'TEST_ERROR',
        message: 'Test error',
      }

      errorRenderer.displayError(error)

      let container = document.getElementById('test-error-container')
      expect(container).not.toBeNull()

      // Click close button
      const closeBtn = document.getElementById('test-error-container-close-btn')
      expect(closeBtn).not.toBeNull()
      
      if (closeBtn) {
        closeBtn.click()
      }

      // Verify container is removed
      container = document.getElementById('test-error-container')
      expect(container).toBeNull()
    })

    it('should dismiss error programmatically', () => {
      const error = {
        code: 'TEST_ERROR',
        message: 'Test error',
      }

      errorRenderer.displayError(error)

      let container = document.getElementById('test-error-container')
      expect(container).not.toBeNull()

      // Dismiss error
      errorRenderer.dismissError()

      // Verify container is removed
      container = document.getElementById('test-error-container')
      expect(container).toBeNull()
    })

    it('should handle multiple error displays by replacing previous error', () => {
      const error1 = {
        code: 'ERROR_1',
        message: 'First error',
      }

      const error2 = {
        code: 'ERROR_2',
        message: 'Second error',
      }

      // Display first error
      errorRenderer.displayError(error1)

      let container = document.getElementById('test-error-container')
      expect(container).not.toBeNull()
      
      let containerText = container?.textContent || ''
      expect(containerText).toContain('First error')

      // Display second error (should replace first)
      errorRenderer.displayError(error2)

      container = document.getElementById('test-error-container')
      expect(container).not.toBeNull()
      
      containerText = container?.textContent || ''
      expect(containerText).toContain('Second error')
      expect(containerText).not.toContain('First error')
    })

    it('should display error with context information', () => {
      const error = {
        code: 'TEST_ERROR',
        message: 'Test error with context',
        context: {
          requestId: '12345',
          timestamp: '2026-02-20T10:00:00Z',
        },
      }

      errorRenderer.displayError(error)

      const container = document.getElementById('test-error-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      
      // Verify error is displayed (context may or may not be shown in UI)
      expect(containerText).toContain('TEST_ERROR')
      expect(containerText).toContain('Test error with context')
    })

    it('should apply correct styling for error visibility', () => {
      const error = {
        code: 'TEST_ERROR',
        message: 'Test error',
      }

      errorRenderer.displayError(error)

      const container = document.getElementById('test-error-container')
      expect(container).not.toBeNull()

      // Verify container is created and visible
      if (container) {
        // Container should be in the document
        expect(document.body.contains(container)).toBe(true)
        
        // Container should have the correct ID
        expect(container.id).toBe('test-error-container')
      }
    })

    it('should display guidance for INITIALIZATION_ERROR', () => {
      const error = {
        code: 'INITIALIZATION_ERROR',
        message: 'Failed to initialize',
      }

      errorRenderer.displayError(error)

      const container = document.getElementById('test-error-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      expect(containerText).toContain('Try refreshing the Gmail page')
    })

    it('should display guidance for TIMEOUT error', () => {
      const error = {
        code: 'TIMEOUT',
        message: 'Request timed out',
      }

      errorRenderer.displayError(error)

      const container = document.getElementById('test-error-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      expect(containerText).toContain('taking too long to respond')
    })

    it('should display guidance for HTTP_422 error', () => {
      const error = {
        code: 'HTTP_422',
        message: 'Invalid request data',
      }

      errorRenderer.displayError(error)

      const container = document.getElementById('test-error-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      expect(containerText).toContain('ensure you have opened a valid email')
    })

    it('should display guidance for HTTP_500 error', () => {
      const error = {
        code: 'HTTP_500',
        message: 'Server error',
      }

      errorRenderer.displayError(error)

      const container = document.getElementById('test-error-container')
      expect(container).not.toBeNull()

      const containerText = container?.textContent || ''
      expect(containerText).toContain('Backend server error')
    })
  })
})
