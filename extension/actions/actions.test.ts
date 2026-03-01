/** Unit tests for TaskActionHandler */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { TaskActionHandler, MeetingPrepDocument } from './actions'
import { TaskDisplayData, Priority, TaskState } from '../ui/ui'

describe('TaskActionHandler', () => {
  let tasks: TaskDisplayData[]
  let handler: TaskActionHandler
  let onTasksUpdatedMock: ReturnType<typeof vi.fn>

  beforeEach(() => {
    // Create sample tasks
    tasks = [
      {
        id: 'task-1',
        title: 'Complete project proposal',
        description: 'Write and submit the Q1 project proposal',
        deadline: '2026-02-20T10:00:00Z',
        owner: 'john@example.com',
        confidence: 0.85,
        priority: Priority.High,
        state: TaskState.Scheduled,
        calendarBlockId: 'cal-123',
      },
      {
        id: 'task-2',
        title: 'Review code changes',
        description: 'Review PR #456 for the new feature',
        deadline: '2026-02-18T15:00:00Z',
        owner: 'jane@example.com',
        confidence: 0.92,
        priority: Priority.Medium,
        state: TaskState.Scheduled,
      },
      {
        id: 'task-3',
        title: 'Schedule team meeting',
        description: 'Organize sync with the design team',
        deadline: '2026-02-19T14:00:00Z',
        owner: 'bob@example.com',
        confidence: 0.65,
        priority: Priority.Low,
        state: TaskState.ManualReview,
      },
    ]

    // Create mock callback
    onTasksUpdatedMock = vi.fn()

    // Create handler instance
    handler = new TaskActionHandler(tasks, onTasksUpdatedMock)
  })

  describe('adjustDeadline', () => {
    it('should update task deadline when valid task ID is provided', () => {
      // Arrange
      const taskId = 'task-1'
      const newDeadline = new Date('2026-02-25T12:00:00Z')

      // Act
      handler.adjustDeadline(taskId, newDeadline)

      // Assert
      const updatedTask = tasks.find(t => t.id === taskId)
      expect(updatedTask).toBeDefined()
      expect(updatedTask!.deadline).toBe(newDeadline.toISOString())
    })

    it('should call onTasksUpdated callback when deadline is adjusted', () => {
      // Arrange
      const taskId = 'task-2'
      const newDeadline = new Date('2026-02-22T09:00:00Z')

      // Act
      handler.adjustDeadline(taskId, newDeadline)

      // Assert
      expect(onTasksUpdatedMock).toHaveBeenCalledTimes(1)
      expect(onTasksUpdatedMock).toHaveBeenCalledWith(tasks)
    })

    it('should handle invalid task ID gracefully', () => {
      // Arrange
      const invalidTaskId = 'non-existent-task'
      const newDeadline = new Date('2026-02-25T12:00:00Z')
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      // Act
      handler.adjustDeadline(invalidTaskId, newDeadline)

      // Assert
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        `Task with id ${invalidTaskId} not found`
      )
      expect(onTasksUpdatedMock).not.toHaveBeenCalled()

      consoleErrorSpy.mockRestore()
    })

    it('should preserve other task properties when adjusting deadline', () => {
      // Arrange
      const taskId = 'task-3'
      const originalTask = { ...tasks.find(t => t.id === taskId)! }
      const newDeadline = new Date('2026-02-28T16:00:00Z')

      // Act
      handler.adjustDeadline(taskId, newDeadline)

      // Assert
      const updatedTask = tasks.find(t => t.id === taskId)!
      expect(updatedTask.title).toBe(originalTask.title)
      expect(updatedTask.description).toBe(originalTask.description)
      expect(updatedTask.owner).toBe(originalTask.owner)
      expect(updatedTask.confidence).toBe(originalTask.confidence)
      expect(updatedTask.priority).toBe(originalTask.priority)
      expect(updatedTask.state).toBe(originalTask.state)
    })
  })

  describe('discardTask', () => {
    it('should remove task from array when valid task ID is provided', () => {
      // Arrange
      const taskId = 'task-2'
      const initialLength = tasks.length

      // Act
      handler.discardTask(taskId)

      // Assert
      expect(tasks.length).toBe(initialLength - 1)
      expect(tasks.find(t => t.id === taskId)).toBeUndefined()
    })

    it('should call onTasksUpdated callback when task is discarded', () => {
      // Arrange
      const taskId = 'task-1'

      // Act
      handler.discardTask(taskId)

      // Assert
      expect(onTasksUpdatedMock).toHaveBeenCalledTimes(1)
      expect(onTasksUpdatedMock).toHaveBeenCalledWith(tasks)
    })

    it('should handle invalid task ID gracefully', () => {
      // Arrange
      const invalidTaskId = 'non-existent-task'
      const initialLength = tasks.length
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      // Act
      handler.discardTask(invalidTaskId)

      // Assert
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        `Task with id ${invalidTaskId} not found`
      )
      expect(tasks.length).toBe(initialLength)
      expect(onTasksUpdatedMock).not.toHaveBeenCalled()

      consoleErrorSpy.mockRestore()
    })

    it('should not affect other tasks when discarding one task', () => {
      // Arrange
      const taskIdToDiscard = 'task-2'
      const otherTaskIds = tasks
        .filter(t => t.id !== taskIdToDiscard)
        .map(t => t.id)

      // Act
      handler.discardTask(taskIdToDiscard)

      // Assert
      otherTaskIds.forEach(id => {
        expect(tasks.find(t => t.id === id)).toBeDefined()
      })
    })
  })

  describe('read-only enforcement', () => {
    it('should not allow editing of task title', () => {
      // This test verifies that the implementation doesn't provide
      // any methods to edit the title field
      const taskId = 'task-1'
      const task = tasks.find(t => t.id === taskId)!
      const originalTitle = task.title

      // Verify no method exists to edit title
      expect(handler).not.toHaveProperty('editTitle')
      expect(handler).not.toHaveProperty('updateTitle')
      expect(handler).not.toHaveProperty('setTitle')

      // Verify title remains unchanged
      expect(task.title).toBe(originalTitle)
    })

    it('should not allow editing of task description', () => {
      // This test verifies that the implementation doesn't provide
      // any methods to edit the description field
      const taskId = 'task-2'
      const task = tasks.find(t => t.id === taskId)!
      const originalDescription = task.description

      // Verify no method exists to edit description
      expect(handler).not.toHaveProperty('editDescription')
      expect(handler).not.toHaveProperty('updateDescription')
      expect(handler).not.toHaveProperty('setDescription')

      // Verify description remains unchanged
      expect(task.description).toBe(originalDescription)
    })

    it('should not allow editing of task owner', () => {
      // This test verifies that the implementation doesn't provide
      // any methods to edit the owner field
      const taskId = 'task-3'
      const task = tasks.find(t => t.id === taskId)!
      const originalOwner = task.owner

      // Verify no method exists to edit owner
      expect(handler).not.toHaveProperty('editOwner')
      expect(handler).not.toHaveProperty('updateOwner')
      expect(handler).not.toHaveProperty('setOwner')
      expect(handler).not.toHaveProperty('changeOwner')

      // Verify owner remains unchanged
      expect(task.owner).toBe(originalOwner)
    })

    it('should only expose adjustDeadline and discardTask as modification methods', () => {
      // Get all methods of the handler
      const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(handler))
        .filter(name => typeof (handler as any)[name] === 'function')
        .filter(name => name !== 'constructor')

      // Public modification methods should only be adjustDeadline and discardTask
      const publicModificationMethods = methods.filter(
        name => !name.startsWith('_') && 
        (name.includes('adjust') || name.includes('discard') || 
         name.includes('edit') || name.includes('update') || 
         name.includes('set') || name.includes('change'))
      )

      // Should only have adjustDeadline and discardTask (and export methods for Task 18)
      expect(publicModificationMethods).toContain('adjustDeadline')
      expect(publicModificationMethods).toContain('discardTask')
      
      // Should not have any edit/update/set/change methods for title/description/owner
      const forbiddenMethods = publicModificationMethods.filter(
        name => 
          (name.toLowerCase().includes('title') ||
           name.toLowerCase().includes('description') ||
           name.toLowerCase().includes('owner')) &&
          name !== 'adjustDeadline' &&
          name !== 'discardTask'
      )
      
      expect(forbiddenMethods).toHaveLength(0)
    })
  })

  describe('attachEventListeners', () => {
    beforeEach(() => {
      // Set up a minimal DOM structure
      document.body.innerHTML = `
        <div data-task-id="task-1">
          <div>Task 1 Title</div>
          <div>Task 1 Description</div>
        </div>
        <div data-task-id="task-2">
          <div>Task 2 Title</div>
          <div>Task 2 Description</div>
        </div>
      `
    })

    it('should add deadline adjustment buttons to task cards', () => {
      // Act
      handler.attachEventListeners()

      // Assert
      const task1Card = document.querySelector('[data-task-id="task-1"]')
      const task2Card = document.querySelector('[data-task-id="task-2"]')

      expect(task1Card?.querySelector('.deadline-adjust-btn')).toBeTruthy()
      expect(task2Card?.querySelector('.deadline-adjust-btn')).toBeTruthy()
    })

    it('should add discard buttons to task cards', () => {
      // Act
      handler.attachEventListeners()

      // Assert
      const task1Card = document.querySelector('[data-task-id="task-1"]')
      const task2Card = document.querySelector('[data-task-id="task-2"]')

      expect(task1Card?.querySelector('.discard-btn')).toBeTruthy()
      expect(task2Card?.querySelector('.discard-btn')).toBeTruthy()
    })

    it('should make task cards read-only', () => {
      // Act
      handler.attachEventListeners()

      // Assert
      const task1Card = document.querySelector('[data-task-id="task-1"]') as HTMLElement
      const task2Card = document.querySelector('[data-task-id="task-2"]') as HTMLElement

      expect(task1Card.contentEditable).toBe('false')
      expect(task2Card.contentEditable).toBe('false')
    })

    it('should not add duplicate buttons when called multiple times', () => {
      // Act
      handler.attachEventListeners()
      handler.attachEventListeners()

      // Assert
      const task1Card = document.querySelector('[data-task-id="task-1"]')
      const adjustButtons = task1Card?.querySelectorAll('.deadline-adjust-btn')
      const discardButtons = task1Card?.querySelectorAll('.discard-btn')

      expect(adjustButtons?.length).toBe(1)
      expect(discardButtons?.length).toBe(1)
    })
  })

  describe('integration scenarios', () => {
    it('should handle multiple deadline adjustments on the same task', () => {
      // Arrange
      const taskId = 'task-1'
      const deadline1 = new Date('2026-02-25T10:00:00Z')
      const deadline2 = new Date('2026-02-26T14:00:00Z')
      const deadline3 = new Date('2026-02-27T09:00:00Z')

      // Act
      handler.adjustDeadline(taskId, deadline1)
      handler.adjustDeadline(taskId, deadline2)
      handler.adjustDeadline(taskId, deadline3)

      // Assert
      const task = tasks.find(t => t.id === taskId)!
      expect(task.deadline).toBe(deadline3.toISOString())
      expect(onTasksUpdatedMock).toHaveBeenCalledTimes(3)
    })

    it('should handle discarding multiple tasks sequentially', () => {
      // Arrange
      const initialLength = tasks.length

      // Act
      handler.discardTask('task-1')
      handler.discardTask('task-2')

      // Assert
      expect(tasks.length).toBe(initialLength - 2)
      expect(tasks.find(t => t.id === 'task-1')).toBeUndefined()
      expect(tasks.find(t => t.id === 'task-2')).toBeUndefined()
      expect(tasks.find(t => t.id === 'task-3')).toBeDefined()
    })

    it('should work without onTasksUpdated callback', () => {
      // Arrange
      const handlerWithoutCallback = new TaskActionHandler(tasks)
      const taskId = 'task-1'
      const newDeadline = new Date('2026-02-25T12:00:00Z')

      // Act & Assert - should not throw
      expect(() => {
        handlerWithoutCallback.adjustDeadline(taskId, newDeadline)
      }).not.toThrow()

      expect(() => {
        handlerWithoutCallback.discardTask('task-2')
      }).not.toThrow()
    })
  })
})

// Property-based tests for export functionality
import * as fc from 'fast-check'

describe('Export Functionality - Property Tests', () => {
  // Feature: ai-execution-agent, Property 19: CSV Export Field Completeness
  describe('Property 19: CSV Export Field Completeness', () => {
    /**
     * Property: For any CSV export of tasks, each row should contain all required fields:
     * title, description, deadline, owner, priority, and confidence
     * Validates: Requirements 11.3
     */
    it('should include all required fields in CSV export for any task set', () => {
      fc.assert(
        fc.property(
          // Generate arbitrary task arrays
          fc.array(
            fc.record({
              id: fc.uuid(),
              title: fc.string({ minLength: 1, maxLength: 200 }),
              description: fc.string({ minLength: 1, maxLength: 2000 }),
              deadline: fc.date().map(d => d.toISOString()),
              owner: fc.emailAddress(),
              confidence: fc.float({ min: 0.0, max: 1.0 }),
              priority: fc.constantFrom(Priority.Low, Priority.Medium, Priority.High),
              state: fc.constantFrom(
                TaskState.Scheduled,
                TaskState.ManualReview,
                TaskState.SchedulingConflict,
                TaskState.Discarded
              ),
              calendarBlockId: fc.option(fc.uuid(), { nil: undefined }),
            }),
            { minLength: 1, maxLength: 50 }
          ),
          (tasks) => {
            // Create a mock DOM environment for the export
            const originalCreateElement = document.createElement.bind(document)
            const originalCreateObjectURL = URL.createObjectURL
            const originalRevokeObjectURL = URL.revokeObjectURL
            
            let capturedCSVContent = ''
            let blobCreated = false

            // Mock Blob to capture CSV content
            const OriginalBlob = global.Blob
            global.Blob = class MockBlob extends OriginalBlob {
              constructor(parts: BlobPart[], options?: BlobPropertyBag) {
                super(parts, options)
                if (options?.type === 'text/csv;charset=utf-8;') {
                  capturedCSVContent = parts[0] as string
                  blobCreated = true
                }
              }
            } as any

            // Mock URL methods
            URL.createObjectURL = vi.fn(() => 'mock-url')
            URL.revokeObjectURL = vi.fn()

            // Mock document.createElement to intercept link creation
            let linkClicked = false
            document.createElement = vi.fn((tagName: string) => {
              const element = originalCreateElement(tagName)
              if (tagName === 'a') {
                element.click = vi.fn(() => {
                  linkClicked = true
                })
              }
              return element
            }) as any

            try {
              // Create handler and export
              const handler = new TaskActionHandler(tasks)
              handler.exportTasksToCSV(tasks)

              // Verify blob was created
              expect(blobCreated).toBe(true)
              expect(linkClicked).toBe(true)

              // Parse CSV content
              const lines = capturedCSVContent.split('\n')
              expect(lines.length).toBeGreaterThan(0)

              // Verify header
              const header = lines[0]
              expect(header).toContain('Title')
              expect(header).toContain('Description')
              expect(header).toContain('Deadline')
              expect(header).toContain('Owner')
              expect(header).toContain('Priority')
              expect(header).toContain('Confidence')

              // Verify each task row contains all fields
              for (let i = 0; i < tasks.length; i++) {
                const task = tasks[i]
                const row = lines[i + 1] // +1 to skip header

                // Parse CSV row (handle quoted fields)
                const parseCSVRow = (csvRow: string): string[] => {
                  const fields: string[] = []
                  let currentField = ''
                  let inQuotes = false

                  for (let j = 0; j < csvRow.length; j++) {
                    const char = csvRow[j]
                    const nextChar = csvRow[j + 1]

                    if (char === '"' && nextChar === '"' && inQuotes) {
                      // Escaped quote
                      currentField += '"'
                      j++ // Skip next quote
                    } else if (char === '"') {
                      // Toggle quote mode
                      inQuotes = !inQuotes
                    } else if (char === ',' && !inQuotes) {
                      // Field separator
                      fields.push(currentField)
                      currentField = ''
                    } else {
                      currentField += char
                    }
                  }
                  fields.push(currentField) // Add last field
                  return fields
                }

                const fields = parseCSVRow(row)

                // Verify we have 6 fields (title, description, deadline, owner, priority, confidence)
                expect(fields.length).toBe(6)

                // Verify each field is present (not empty after parsing)
                // Note: We check that the CSV contains the data, not exact match due to escaping
                expect(fields[0]).toBeTruthy() // Title
                expect(fields[1]).toBeTruthy() // Description
                expect(fields[2]).toBeTruthy() // Deadline
                expect(fields[3]).toBeTruthy() // Owner
                expect(fields[4]).toBeTruthy() // Priority
                expect(fields[5]).toBeTruthy() // Confidence

                // Verify the actual values are present in the row (accounting for CSV escaping)
                const rowContent = row.toLowerCase()
                expect(rowContent).toContain(task.priority.toLowerCase())
              }
            } finally {
              // Restore mocks
              global.Blob = OriginalBlob
              URL.createObjectURL = originalCreateObjectURL
              URL.revokeObjectURL = originalRevokeObjectURL
              document.createElement = originalCreateElement as any
            }
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should handle special characters in CSV export correctly', () => {
      fc.assert(
        fc.property(
          // Generate tasks with special characters
          fc.array(
            fc.record({
              id: fc.uuid(),
              title: fc.string({ minLength: 1, maxLength: 100 }).map(s => 
                s + fc.sample(fc.constantFrom(',', '"', '\n', '\r'), 1)[0]
              ),
              description: fc.string({ minLength: 1, maxLength: 200 }).map(s => 
                s + fc.sample(fc.constantFrom(',', '"', '\n', '\r'), 1)[0]
              ),
              deadline: fc.date().map(d => d.toISOString()),
              owner: fc.emailAddress(),
              confidence: fc.float({ min: 0.0, max: 1.0 }),
              priority: fc.constantFrom(Priority.Low, Priority.Medium, Priority.High),
              state: fc.constantFrom(
                TaskState.Scheduled,
                TaskState.ManualReview,
                TaskState.SchedulingConflict,
                TaskState.Discarded
              ),
              calendarBlockId: fc.option(fc.uuid(), { nil: undefined }),
            }),
            { minLength: 1, maxLength: 20 }
          ),
          (tasks) => {
            const originalCreateElement = document.createElement.bind(document)
            const originalCreateObjectURL = URL.createObjectURL
            const originalRevokeObjectURL = URL.revokeObjectURL
            
            let capturedCSVContent = ''

            const OriginalBlob = global.Blob
            global.Blob = class MockBlob extends OriginalBlob {
              constructor(parts: BlobPart[], options?: BlobPropertyBag) {
                super(parts, options)
                if (options?.type === 'text/csv;charset=utf-8;') {
                  capturedCSVContent = parts[0] as string
                }
              }
            } as any

            URL.createObjectURL = vi.fn(() => 'mock-url')
            URL.revokeObjectURL = vi.fn()

            document.createElement = vi.fn((tagName: string) => {
              const element = originalCreateElement(tagName)
              if (tagName === 'a') {
                element.click = vi.fn()
              }
              return element
            }) as any

            try {
              const handler = new TaskActionHandler(tasks)
              handler.exportTasksToCSV(tasks)

              // Parse CSV properly - count rows by parsing, not by splitting on newlines
              // because newlines within quoted fields are valid CSV
              const parseCSVRows = (csv: string): string[][] => {
                const rows: string[][] = []
                let currentRow: string[] = []
                let currentField = ''
                let inQuotes = false
                let i = 0

                while (i < csv.length) {
                  const char = csv[i]
                  const nextChar = csv[i + 1]

                  if (char === '"' && nextChar === '"' && inQuotes) {
                    // Escaped quote
                    currentField += '"'
                    i += 2
                  } else if (char === '"') {
                    // Toggle quote mode
                    inQuotes = !inQuotes
                    i++
                  } else if (char === ',' && !inQuotes) {
                    // Field separator
                    currentRow.push(currentField)
                    currentField = ''
                    i++
                  } else if (char === '\n' && !inQuotes) {
                    // Row separator (only when not in quotes)
                    currentRow.push(currentField)
                    if (currentRow.length > 0 && currentRow.some(f => f.length > 0)) {
                      rows.push(currentRow)
                    }
                    currentRow = []
                    currentField = ''
                    i++
                  } else if (char === '\r' && nextChar === '\n' && !inQuotes) {
                    // Windows line ending
                    currentRow.push(currentField)
                    if (currentRow.length > 0 && currentRow.some(f => f.length > 0)) {
                      rows.push(currentRow)
                    }
                    currentRow = []
                    currentField = ''
                    i += 2
                  } else {
                    currentField += char
                    i++
                  }
                }

                // Add last field and row if not empty
                if (currentField.length > 0 || currentRow.length > 0) {
                  currentRow.push(currentField)
                  if (currentRow.some(f => f.length > 0)) {
                    rows.push(currentRow)
                  }
                }

                return rows
              }

              const rows = parseCSVRows(capturedCSVContent)
              
              // Verify we have header + task rows
              expect(rows.length).toBe(tasks.length + 1) // +1 for header

              // Verify header
              expect(rows[0].length).toBe(6)

              // Verify each task row has 6 fields
              for (let i = 1; i < rows.length; i++) {
                expect(rows[i].length).toBe(6)
                // Verify all fields are present (not empty)
                expect(rows[i][0]).toBeTruthy() // Title
                expect(rows[i][1]).toBeTruthy() // Description
                expect(rows[i][2]).toBeTruthy() // Deadline
                expect(rows[i][3]).toBeTruthy() // Owner
                expect(rows[i][4]).toBeTruthy() // Priority
                expect(rows[i][5]).toBeTruthy() // Confidence
              }
            } finally {
              global.Blob = OriginalBlob
              URL.createObjectURL = originalCreateObjectURL
              URL.revokeObjectURL = originalRevokeObjectURL
              document.createElement = originalCreateElement as any
            }
          }
        ),
        { numRuns: 100 }
      )
    })
  })
})

// Unit tests for export functionality
describe('Export Functionality - Unit Tests', () => {
  let tasks: TaskDisplayData[]
  let handler: TaskActionHandler

  beforeEach(() => {
    tasks = [
      {
        id: 'task-1',
        title: 'Complete project proposal',
        description: 'Write and submit the Q1 project proposal',
        deadline: '2026-02-20T10:00:00Z',
        owner: 'john@example.com',
        confidence: 0.85,
        priority: Priority.High,
        state: TaskState.Scheduled,
        calendarBlockId: 'cal-123',
      },
      {
        id: 'task-2',
        title: 'Review code changes',
        description: 'Review PR #456 for the new feature',
        deadline: '2026-02-18T15:00:00Z',
        owner: 'jane@example.com',
        confidence: 0.92,
        priority: Priority.Medium,
        state: TaskState.Scheduled,
      },
    ]

    handler = new TaskActionHandler(tasks)
  })

  describe('exportTasksToCSV', () => {
    it('should generate CSV with correct header', () => {
      // Arrange
      const originalCreateElement = document.createElement.bind(document)
      const originalCreateObjectURL = URL.createObjectURL
      const originalRevokeObjectURL = URL.revokeObjectURL
      
      let capturedCSVContent = ''

      const OriginalBlob = global.Blob
      global.Blob = class MockBlob extends OriginalBlob {
        constructor(parts: BlobPart[], options?: BlobPropertyBag) {
          super(parts, options)
          if (options?.type === 'text/csv;charset=utf-8;') {
            capturedCSVContent = parts[0] as string
          }
        }
      } as any

      URL.createObjectURL = vi.fn(() => 'mock-url')
      URL.revokeObjectURL = vi.fn()

      document.createElement = vi.fn((tagName: string) => {
        const element = originalCreateElement(tagName)
        if (tagName === 'a') {
          element.click = vi.fn()
        }
        return element
      }) as any

      try {
        // Act
        handler.exportTasksToCSV(tasks)

        // Assert
        const lines = capturedCSVContent.split('\n')
        const header = lines[0]
        expect(header).toBe('Title,Description,Deadline,Owner,Priority,Confidence')
      } finally {
        global.Blob = OriginalBlob
        URL.createObjectURL = originalCreateObjectURL
        URL.revokeObjectURL = originalRevokeObjectURL
        document.createElement = originalCreateElement as any
      }
    })

    it('should include all task data in CSV rows', () => {
      // Arrange
      const originalCreateElement = document.createElement.bind(document)
      const originalCreateObjectURL = URL.createObjectURL
      const originalRevokeObjectURL = URL.revokeObjectURL
      
      let capturedCSVContent = ''

      const OriginalBlob = global.Blob
      global.Blob = class MockBlob extends OriginalBlob {
        constructor(parts: BlobPart[], options?: BlobPropertyBag) {
          super(parts, options)
          if (options?.type === 'text/csv;charset=utf-8;') {
            capturedCSVContent = parts[0] as string
          }
        }
      } as any

      URL.createObjectURL = vi.fn(() => 'mock-url')
      URL.revokeObjectURL = vi.fn()

      document.createElement = vi.fn((tagName: string) => {
        const element = originalCreateElement(tagName)
        if (tagName === 'a') {
          element.click = vi.fn()
        }
        return element
      }) as any

      try {
        // Act
        handler.exportTasksToCSV(tasks)

        // Assert
        const content = capturedCSVContent
        expect(content).toContain('Complete project proposal')
        expect(content).toContain('Write and submit the Q1 project proposal')
        expect(content).toContain('john@example.com')
        expect(content).toContain('high')
        expect(content).toContain('0.85')
        expect(content).toContain('Review code changes')
        expect(content).toContain('jane@example.com')
        expect(content).toContain('medium')
        expect(content).toContain('0.92')
      } finally {
        global.Blob = OriginalBlob
        URL.createObjectURL = originalCreateObjectURL
        URL.revokeObjectURL = originalRevokeObjectURL
        document.createElement = originalCreateElement as any
      }
    })

    it('should handle special characters with proper CSV escaping', () => {
      // Arrange
      const tasksWithSpecialChars: TaskDisplayData[] = [
        {
          id: 'task-special',
          title: 'Task with, comma',
          description: 'Description with "quotes"',
          deadline: '2026-02-20T10:00:00Z',
          owner: 'test@example.com',
          confidence: 0.75,
          priority: Priority.High,
          state: TaskState.Scheduled,
        },
      ]

      const originalCreateElement = document.createElement.bind(document)
      const originalCreateObjectURL = URL.createObjectURL
      const originalRevokeObjectURL = URL.revokeObjectURL
      
      let capturedCSVContent = ''

      const OriginalBlob = global.Blob
      global.Blob = class MockBlob extends OriginalBlob {
        constructor(parts: BlobPart[], options?: BlobPropertyBag) {
          super(parts, options)
          if (options?.type === 'text/csv;charset=utf-8;') {
            capturedCSVContent = parts[0] as string
          }
        }
      } as any

      URL.createObjectURL = vi.fn(() => 'mock-url')
      URL.revokeObjectURL = vi.fn()

      document.createElement = vi.fn((tagName: string) => {
        const element = originalCreateElement(tagName)
        if (tagName === 'a') {
          element.click = vi.fn()
        }
        return element
      }) as any

      try {
        // Act
        handler.exportTasksToCSV(tasksWithSpecialChars)

        // Assert
        const lines = capturedCSVContent.split('\n')
        const dataRow = lines[1]
        
        // Fields with commas should be wrapped in quotes
        expect(dataRow).toContain('"Task with, comma"')
        
        // Fields with quotes should have escaped quotes (doubled)
        expect(dataRow).toContain('"Description with ""quotes"""')
      } finally {
        global.Blob = OriginalBlob
        URL.createObjectURL = originalCreateObjectURL
        URL.revokeObjectURL = originalRevokeObjectURL
        document.createElement = originalCreateElement as any
      }
    })

    it('should handle empty task list gracefully', () => {
      // Arrange
      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      // Act
      handler.exportTasksToCSV([])

      // Assert
      expect(consoleWarnSpy).toHaveBeenCalledWith('No tasks to export')

      consoleWarnSpy.mockRestore()
    })

    it('should create download link with correct filename', () => {
      // Arrange
      const originalCreateElement = document.createElement.bind(document)
      const originalCreateObjectURL = URL.createObjectURL
      const originalRevokeObjectURL = URL.revokeObjectURL
      
      let downloadFilename = ''

      URL.createObjectURL = vi.fn(() => 'mock-url')
      URL.revokeObjectURL = vi.fn()

      document.createElement = vi.fn((tagName: string) => {
        const element = originalCreateElement(tagName)
        if (tagName === 'a') {
          element.click = vi.fn()
          // Capture the download attribute
          Object.defineProperty(element, 'download', {
            set: (value: string) => {
              downloadFilename = value
            },
            get: () => downloadFilename,
          })
        }
        return element
      }) as any

      const OriginalBlob = global.Blob
      global.Blob = class MockBlob extends OriginalBlob {
        constructor(parts: BlobPart[], options?: BlobPropertyBag) {
          super(parts, options)
        }
      } as any

      try {
        // Act
        handler.exportTasksToCSV(tasks)

        // Assert
        expect(downloadFilename).toMatch(/^tasks_export_\d{4}-\d{2}-\d{2}\.csv$/)
      } finally {
        global.Blob = OriginalBlob
        URL.createObjectURL = originalCreateObjectURL
        URL.revokeObjectURL = originalRevokeObjectURL
        document.createElement = originalCreateElement as any
      }
    })
  })

  describe('exportMeetingPrepToPDF', () => {
    let meetingPrepDoc: MeetingPrepDocument

    beforeEach(() => {
      meetingPrepDoc = {
        meetingTitle: 'Q1 Planning Meeting',
        meetingTime: '2026-02-20T14:00:00Z',
        contextSummary: 'Discuss Q1 goals and objectives for the team',
        talkingPoints: [
          'Review Q4 performance',
          'Set Q1 OKRs',
          'Discuss resource allocation',
        ],
        questions: [
          'What are the top priorities?',
          'Do we have sufficient budget?',
          'What are the key risks?',
        ],
        risks: [
          'Timeline may be too aggressive',
          'Resource constraints',
        ],
      }
    })

    it('should generate HTML with meeting title', () => {
      // Arrange
      const originalOpen = window.open
      const originalCreateObjectURL = URL.createObjectURL
      const originalRevokeObjectURL = URL.revokeObjectURL
      let capturedHTML = ''

      const OriginalBlob = global.Blob
      global.Blob = class MockBlob extends OriginalBlob {
        constructor(parts: BlobPart[], options?: BlobPropertyBag) {
          super(parts, options)
          if (options?.type === 'text/html') {
            capturedHTML = parts[0] as string
          }
        }
      } as any

      URL.createObjectURL = vi.fn(() => 'mock-url')
      URL.revokeObjectURL = vi.fn()
      window.open = vi.fn(() => null)

      try {
        // Act
        handler.exportMeetingPrepToPDF(meetingPrepDoc)

        // Assert
        expect(capturedHTML).toContain('Q1 Planning Meeting')
        expect(capturedHTML).toContain('<h1>Q1 Planning Meeting</h1>')
      } finally {
        global.Blob = OriginalBlob
        URL.createObjectURL = originalCreateObjectURL
        URL.revokeObjectURL = originalRevokeObjectURL
        window.open = originalOpen
      }
    })

    it('should include all meeting prep sections', () => {
      // Arrange
      const originalOpen = window.open
      const originalCreateObjectURL = URL.createObjectURL
      const originalRevokeObjectURL = URL.revokeObjectURL
      let capturedHTML = ''

      const OriginalBlob = global.Blob
      global.Blob = class MockBlob extends OriginalBlob {
        constructor(parts: BlobPart[], options?: BlobPropertyBag) {
          super(parts, options)
          if (options?.type === 'text/html') {
            capturedHTML = parts[0] as string
          }
        }
      } as any

      URL.createObjectURL = vi.fn(() => 'mock-url')
      URL.revokeObjectURL = vi.fn()
      window.open = vi.fn(() => null)

      try {
        // Act
        handler.exportMeetingPrepToPDF(meetingPrepDoc)

        // Assert
        expect(capturedHTML).toContain('Context Summary')
        expect(capturedHTML).toContain('Key Talking Points')
        expect(capturedHTML).toContain('Questions to Ask')
        expect(capturedHTML).toContain('Potential Risks or Concerns')
        
        // Check content
        expect(capturedHTML).toContain('Discuss Q1 goals and objectives')
        expect(capturedHTML).toContain('Review Q4 performance')
        expect(capturedHTML).toContain('What are the top priorities?')
        expect(capturedHTML).toContain('Timeline may be too aggressive')
      } finally {
        global.Blob = OriginalBlob
        URL.createObjectURL = originalCreateObjectURL
        URL.revokeObjectURL = originalRevokeObjectURL
        window.open = originalOpen
      }
    })

    it('should escape HTML special characters to prevent XSS', () => {
      // Arrange
      const maliciousPrepDoc: MeetingPrepDocument = {
        meetingTitle: '<script>alert("xss")</script>',
        meetingTime: '2026-02-20T14:00:00Z',
        contextSummary: '<img src=x onerror=alert(1)>',
        talkingPoints: ['<b>Bold</b> text'],
        questions: ['Question with <script>'],
        risks: ['Risk with <iframe>'],
      }

      const originalOpen = window.open
      const originalCreateObjectURL = URL.createObjectURL
      const originalRevokeObjectURL = URL.revokeObjectURL
      let capturedHTML = ''

      const OriginalBlob = global.Blob
      global.Blob = class MockBlob extends OriginalBlob {
        constructor(parts: BlobPart[], options?: BlobPropertyBag) {
          super(parts, options)
          if (options?.type === 'text/html') {
            capturedHTML = parts[0] as string
          }
        }
      } as any

      URL.createObjectURL = vi.fn(() => 'mock-url')
      URL.revokeObjectURL = vi.fn()
      window.open = vi.fn(() => null)

      try {
        // Act
        handler.exportMeetingPrepToPDF(maliciousPrepDoc)

        // Assert
        // Script tags should be escaped
        expect(capturedHTML).not.toContain('<script>alert("xss")</script>')
        expect(capturedHTML).toContain('&lt;script&gt;')
        
        // Other HTML tags should be escaped
        expect(capturedHTML).not.toContain('<img src=x onerror=alert(1)>')
        expect(capturedHTML).not.toContain('<iframe>')
      } finally {
        global.Blob = OriginalBlob
        URL.createObjectURL = originalCreateObjectURL
        URL.revokeObjectURL = originalRevokeObjectURL
        window.open = originalOpen
      }
    })

    it('should handle popup blocker gracefully', () => {
      // Arrange
      const originalOpen = window.open
      const originalCreateObjectURL = URL.createObjectURL
      const originalRevokeObjectURL = URL.revokeObjectURL
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      URL.createObjectURL = vi.fn(() => 'mock-url')
      URL.revokeObjectURL = vi.fn()
      window.open = vi.fn(() => null) // Simulate blocked popup

      const OriginalBlob = global.Blob
      global.Blob = class MockBlob extends OriginalBlob {
        constructor(parts: BlobPart[], options?: BlobPropertyBag) {
          super(parts, options)
        }
      } as any

      try {
        // Act
        handler.exportMeetingPrepToPDF(meetingPrepDoc)

        // Assert
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          'Failed to open print window - popup may be blocked'
        )
      } finally {
        global.Blob = OriginalBlob
        URL.createObjectURL = originalCreateObjectURL
        URL.revokeObjectURL = originalRevokeObjectURL
        window.open = originalOpen
        consoleErrorSpy.mockRestore()
      }
    })

    it('should format prep document with proper styling', () => {
      // Arrange
      const originalOpen = window.open
      const originalCreateObjectURL = URL.createObjectURL
      const originalRevokeObjectURL = URL.revokeObjectURL
      let capturedHTML = ''

      const OriginalBlob = global.Blob
      global.Blob = class MockBlob extends OriginalBlob {
        constructor(parts: BlobPart[], options?: BlobPropertyBag) {
          super(parts, options)
          if (options?.type === 'text/html') {
            capturedHTML = parts[0] as string
          }
        }
      } as any

      URL.createObjectURL = vi.fn(() => 'mock-url')
      URL.revokeObjectURL = vi.fn()
      window.open = vi.fn(() => null)

      try {
        // Act
        handler.exportMeetingPrepToPDF(meetingPrepDoc)

        // Assert
        // Check for CSS styling
        expect(capturedHTML).toContain('<style>')
        expect(capturedHTML).toContain('font-family')
        expect(capturedHTML).toContain('@media print')
        
        // Check for proper HTML structure
        expect(capturedHTML).toContain('<!DOCTYPE html>')
        expect(capturedHTML).toContain('<html>')
        expect(capturedHTML).toContain('</html>')
      } finally {
        global.Blob = OriginalBlob
        URL.createObjectURL = originalCreateObjectURL
        URL.revokeObjectURL = originalRevokeObjectURL
        window.open = originalOpen
      }
    })
  })
})
