/** Main execution controller for the AI Execution Agent Chrome Extension. */

import { GmailDOMExtractor, EmailContent } from './content/content'
import { BackendAPIClient, RunAgentRequest, RunAgentResponse, BackendAPIError } from './api/api'
import { TaskBoardRenderer, TaskDisplayData, LogEntry, ErrorDisplayRenderer } from './ui/ui'
import { TaskActionHandler } from './actions/actions'

/**
 * Main controller class that orchestrates the execution flow
 * Requirements: 15.5, 16.3
 */
export class ExecutionController {
  private extractor: GmailDOMExtractor
  private apiClient: BackendAPIClient
  private renderer: TaskBoardRenderer
  private errorRenderer: ErrorDisplayRenderer
  private actionHandler: TaskActionHandler | null = null
  private isExecuting = false

  constructor(backendUrl: string) {
    this.extractor = new GmailDOMExtractor()
    this.apiClient = new BackendAPIClient(backendUrl)
    this.renderer = new TaskBoardRenderer()
    this.errorRenderer = new ErrorDisplayRenderer()
  }

  /**
   * Initialize the extension - inject button and wire event listeners
   * Requirements: 15.5
   */
  initialize(): void {
    try {
      // Inject the "Run Agent" button into Gmail UI
      this.extractor.injectRunAgentButton()

      // Wire the button click event
      this.wireRunAgentButton()

      console.log('AI Execution Agent initialized successfully')
    } catch (error) {
      console.error('Failed to initialize AI Execution Agent:', error)
      this.displayError({
        code: 'INITIALIZATION_ERROR',
        message: error instanceof Error ? error.message : 'Failed to initialize extension',
      })
    }
  }

  /**
   * Helper method to display errors
   * Requirements: 16.3
   */
  private displayError(errorDetail: { code: string; message: string; context?: Record<string, unknown> }): void {
    this.errorRenderer.displayError(errorDetail)
  }

  /**
   * Wire the "Run Agent" button to the execution flow
   * Requirements: 15.5
   */
  private wireRunAgentButton(): void {
    const button = document.getElementById('ai-agent-run-button')
    
    if (!button) {
      console.error('Run Agent button not found in DOM')
      return
    }

    // Add click event listener
    button.addEventListener('click', async () => {
      await this.handleRunAgentClick()
    })

    console.log('Run Agent button wired to execution flow')
  }

  /**
   * Handle the "Run Agent" button click
   * Requirements: 15.5, 16.3
   */
  private async handleRunAgentClick(): Promise<void> {
    // Prevent multiple simultaneous executions
    if (this.isExecuting) {
      console.warn('Agent execution already in progress')
      return
    }

    this.isExecuting = true

    try {
      // Step 1: Extract email content
      console.log('Extracting email content...')
      const emailContent = this.extractEmailContent()

      // Step 2: Call backend API
      console.log('Calling backend API...')
      const response = await this.callBackendAPI(emailContent)

      // Step 3: Render results
      console.log('Rendering results...')
      this.renderResults(response)

      console.log('Agent execution completed successfully')
    } catch (error) {
      console.error('Agent execution failed:', error)
      this.handleExecutionError(error)
    } finally {
      this.isExecuting = false
    }
  }

  /**
   * Extract email content from Gmail DOM
   * Requirements: 15.5
   */
  private extractEmailContent(): EmailContent {
    try {
      const emailContent = this.extractor.extractEmailContent()

      // Validate that we have at least some content
      if (!emailContent.subject && !emailContent.body) {
        throw new Error('No email content found. Please open an email and try again.')
      }

      return emailContent
    } catch (error) {
      throw new Error(
        `Failed to extract email content: ${error instanceof Error ? error.message : String(error)}`
      )
    }
  }

  /**
   * Call the backend API with extracted email content
   * Requirements: 15.5
   */
  private async callBackendAPI(emailContent: EmailContent): Promise<RunAgentResponse> {
    try {
      // Build the request
      const request: RunAgentRequest = {
        emailContent,
        userTimezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        calendarId: 'primary', // Default to primary calendar
      }

      // Call the backend
      const response = await this.apiClient.runAgent(request)

      return response
    } catch (error) {
      if (error instanceof BackendAPIError) {
        throw error
      }
      throw new Error(
        `Backend API call failed: ${error instanceof Error ? error.message : String(error)}`
      )
    }
  }

  /**
   * Render the execution results (task board, feedback, logs)
   * Requirements: 15.5
   */
  private renderResults(response: RunAgentResponse): void {
    try {
      // Convert response tasks to display format
      const tasks: TaskDisplayData[] = response.tasks.map(task => ({
        id: task.id,
        title: task.title,
        description: task.description,
        deadline: task.deadline,
        owner: task.owner,
        confidence: task.confidence,
        priority: task.priority as any, // Type conversion
        state: task.state as any, // Type conversion
        calendarBlockId: task.calendarBlockId,
      }))

      // Render task board
      this.renderer.renderTaskBoard(tasks)

      // Render feedback panel
      this.renderer.renderFeedbackPanel(response.stats)

      // Convert logs to include level field
      const logsWithLevel: LogEntry[] = response.logs.map(log => ({
        timestamp: log.timestamp,
        message: log.message,
        level: 'info' as const, // Default to info level
      }))

      // Check for errors in response and add them to logs
      if (response.errors && response.errors.length > 0) {
        response.errors.forEach(error => {
          logsWithLevel.push({
            timestamp: new Date().toISOString(),
            message: `Error: ${error.message}`,
            level: 'error',
          })
        })
      }

      // Render execution log
      this.renderer.renderExecutionLog(logsWithLevel)

      // Initialize action handler for task interactions
      this.actionHandler = new TaskActionHandler(tasks, (updatedTasks) => {
        // Re-render task board when tasks are updated
        this.renderer.renderTaskBoard(updatedTasks)
      })

      // Attach event listeners to task elements
      // Use setTimeout to ensure DOM is fully rendered
      setTimeout(() => {
        if (this.actionHandler) {
          this.actionHandler.attachEventListeners()
          // Wire export functionality to UI buttons
          this.wireExportButtons(tasks, response)
        }
      }, 100)

      console.log('Results rendered successfully')
    } catch (error) {
      throw new Error(
        `Failed to render results: ${error instanceof Error ? error.message : String(error)}`
      )
    }
  }

  /**
   * Handle execution errors and display them to the user
   * Requirements: 16.3
   */
  private handleExecutionError(error: unknown): void {
    let errorDetail: { code: string; message: string; context?: Record<string, unknown> }

    if (error instanceof BackendAPIError) {
      errorDetail = error.errorDetail
    } else if (error instanceof Error) {
      errorDetail = {
        code: 'EXECUTION_ERROR',
        message: error.message,
      }
    } else {
      errorDetail = {
        code: 'UNKNOWN_ERROR',
        message: String(error),
      }
    }

    this.errorRenderer.displayError(errorDetail)
  }

  /**
   * Wire export functionality to UI buttons
   * Requirements: 11.1
   */
  private wireExportButtons(tasks: TaskDisplayData[], response: RunAgentResponse): void {
    // Add CSV export button to task board
    const taskBoardContainer = document.getElementById('ai-agent-task-board')
    if (taskBoardContainer && !document.getElementById('csv-export-btn')) {
      const exportBtn = document.createElement('button')
      exportBtn.id = 'csv-export-btn'
      exportBtn.style.cssText = `
        margin: 16px;
        padding: 8px 16px;
        background: #34a853;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        font-family: 'Google Sans', Roboto, Arial, sans-serif;
      `
      exportBtn.textContent = '📥 Export Tasks to CSV'
      exportBtn.addEventListener('click', () => {
        if (this.actionHandler) {
          this.actionHandler.exportTasksToCSV(tasks)
        }
      })
      
      // Insert at the top of the task board (after header)
      const header = taskBoardContainer.firstElementChild
      if (header && header.nextSibling) {
        taskBoardContainer.insertBefore(exportBtn, header.nextSibling)
      } else {
        taskBoardContainer.appendChild(exportBtn)
      }
    }

    // Add PDF export buttons for meeting prep documents
    tasks.forEach(task => {
      // Check if task has meeting prep document in the response
      const taskData = response.tasks.find(t => t.id === task.id)
      if (taskData && (taskData as any).meetingPrep) {
        const taskCard = document.querySelector(`[data-task-id="${task.id}"]`)
        if (taskCard && !taskCard.querySelector('.pdf-export-btn')) {
          const pdfBtn = document.createElement('button')
          pdfBtn.className = 'pdf-export-btn'
          pdfBtn.style.cssText = `
            margin-top: 8px;
            padding: 6px 12px;
            background: #ea4335;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            font-family: 'Google Sans', Roboto, Arial, sans-serif;
          `
          pdfBtn.textContent = '📄 Export Meeting Prep to PDF'
          pdfBtn.addEventListener('click', () => {
            if (this.actionHandler) {
              this.actionHandler.exportMeetingPrepToPDF((taskData as any).meetingPrep)
            }
          })
          
          taskCard.appendChild(pdfBtn)
        }
      }
    })
  }
}

/**
 * Initialize the extension when DOM is ready
 * Requirements: 15.1, 15.2, 15.3, 15.4, 15.5
 */
function initializeExtension(): void {
  // Get backend URL from environment or use default
  const backendUrl = 'https://localhost:8000' // TODO: Make this configurable

  // Create controller instance
  const controller = new ExecutionController(backendUrl)

  // Initialize the extension (inject button and wire events)
  controller.initialize()
}

// Wait for DOM to be ready before initializing
// This ensures we don't execute automatically on page load
// Requirements: 15.1, 15.2
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeExtension)
} else {
  // DOM is already ready
  initializeExtension()
}

// Export for testing
export { initializeExtension }
