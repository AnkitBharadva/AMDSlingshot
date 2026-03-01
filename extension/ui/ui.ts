/** UI rendering for task board, feedback panel, and logs. */

// Export types
export interface TaskDisplayData {
  id: string
  title: string
  description: string
  deadline: string
  owner: string
  confidence: number
  priority: Priority
  state: TaskState
  calendarBlockId?: string
}

export enum Priority {
  Low = 'low',
  Medium = 'medium',
  High = 'high',
}

export enum TaskState {
  Scheduled = 'scheduled',
  ManualReview = 'manual_review',
  SchedulingConflict = 'scheduling_conflict',
  Discarded = 'discarded',
}

export interface FeedbackStats {
  tasksExtracted: number
  calendarBlocksCreated: number
  schedulingConflicts: number
  manualReviewItems: number
}

export interface LogEntry {
  timestamp: string
  message: string
  level: 'info' | 'warning' | 'error'
}

export interface TimelineGroups {
  today: TaskDisplayData[]
  tomorrow: TaskDisplayData[]
  upcoming: TaskDisplayData[]
}

// Export UI renderer class
export class TaskBoardRenderer {
  private containerId: string

  constructor(containerId: string = 'ai-agent-task-board') {
    this.containerId = containerId
  }

  /**
   * Render the task board with all tasks
   */
  renderTaskBoard(tasks: TaskDisplayData[]): void {
    // Get or create container
    let container = document.getElementById(this.containerId)
    if (!container) {
      container = document.createElement('div')
      container.id = this.containerId
      container.style.cssText = `
        position: fixed;
        top: 60px;
        right: 20px;
        width: 400px;
        max-height: 80vh;
        overflow-y: auto;
        background: white;
        border: 1px solid #dadce0;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        z-index: 10000;
        font-family: 'Google Sans', Roboto, Arial, sans-serif;
      `
      document.body.appendChild(container)
    }

    // Clear existing content
    container.innerHTML = ''

    // Add header
    const header = document.createElement('div')
    header.style.cssText = `
      padding: 16px;
      border-bottom: 1px solid #dadce0;
      font-size: 18px;
      font-weight: 500;
      color: #202124;
    `
    header.textContent = 'Task Board'
    container.appendChild(header)

    // Group tasks by timeline
    const groups = this.groupTasksByTimeline(tasks)

    // Render each timeline group
    this.renderTimelineGroup(container, 'Today', groups.today)
    this.renderTimelineGroup(container, 'Tomorrow', groups.tomorrow)
    this.renderTimelineGroup(container, 'Upcoming', groups.upcoming)

    // Show empty state if no tasks
    if (tasks.length === 0) {
      const emptyState = document.createElement('div')
      emptyState.style.cssText = `
        padding: 32px;
        text-align: center;
        color: #5f6368;
        font-size: 14px;
      `
      emptyState.textContent = 'No tasks extracted'
      container.appendChild(emptyState)
    }
  }

  /**
   * Render a timeline group (Today, Tomorrow, Upcoming)
   */
  private renderTimelineGroup(container: HTMLElement, groupName: string, tasks: TaskDisplayData[]): void {
    if (tasks.length === 0) {
      return
    }

    // Group header
    const groupHeader = document.createElement('div')
    groupHeader.style.cssText = `
      padding: 12px 16px;
      background: #f8f9fa;
      font-size: 14px;
      font-weight: 500;
      color: #5f6368;
      border-bottom: 1px solid #dadce0;
    `
    groupHeader.textContent = groupName
    container.appendChild(groupHeader)

    // Render each task in the group
    tasks.forEach(task => {
      this.renderTask(container, task)
    })
  }

  /**
   * Render a single task
   */
  private renderTask(container: HTMLElement, task: TaskDisplayData): void {
    const taskCard = document.createElement('div')
    taskCard.style.cssText = `
      padding: 16px;
      border-bottom: 1px solid #f1f3f4;
      cursor: default;
    `
    taskCard.dataset.taskId = task.id

    // Add visual indicator for manual review tasks
    if (task.state === TaskState.ManualReview) {
      taskCard.style.borderLeft = '4px solid #f9ab00'
      taskCard.style.paddingLeft = '12px'
    } else if (task.state === TaskState.SchedulingConflict) {
      taskCard.style.borderLeft = '4px solid #ea4335'
      taskCard.style.paddingLeft = '12px'
    } else if (task.state === TaskState.Scheduled) {
      taskCard.style.borderLeft = '4px solid #34a853'
      taskCard.style.paddingLeft = '12px'
    }

    // Task title
    const title = document.createElement('div')
    title.style.cssText = `
      font-size: 16px;
      font-weight: 500;
      color: #202124;
      margin-bottom: 8px;
    `
    title.textContent = task.title
    taskCard.appendChild(title)

    // Task description
    const description = document.createElement('div')
    description.style.cssText = `
      font-size: 14px;
      color: #5f6368;
      margin-bottom: 12px;
      line-height: 1.4;
    `
    description.textContent = task.description
    taskCard.appendChild(description)

    // Task metadata row
    const metadataRow = document.createElement('div')
    metadataRow.style.cssText = `
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      font-size: 12px;
      color: #5f6368;
    `

    // Deadline
    const deadline = document.createElement('div')
    deadline.innerHTML = `<strong>Deadline:</strong> ${this.formatDeadline(task.deadline)}`
    metadataRow.appendChild(deadline)

    // Owner
    const owner = document.createElement('div')
    owner.innerHTML = `<strong>Owner:</strong> ${task.owner}`
    metadataRow.appendChild(owner)

    // Priority
    const priority = document.createElement('div')
    priority.innerHTML = `<strong>Priority:</strong> ${this.formatPriority(task.priority)}`
    metadataRow.appendChild(priority)

    // Confidence
    const confidence = document.createElement('div')
    const confidencePercent = Math.round(task.confidence * 100)
    confidence.innerHTML = `<strong>Confidence:</strong> ${confidencePercent}%`
    
    // Color code confidence
    if (task.confidence < 0.7) {
      confidence.style.color = '#f9ab00'
    } else if (task.confidence >= 0.9) {
      confidence.style.color = '#34a853'
    }
    
    metadataRow.appendChild(confidence)

    taskCard.appendChild(metadataRow)

    // State indicator for manual review or scheduling conflict
    if (task.state === TaskState.ManualReview) {
      const stateIndicator = document.createElement('div')
      stateIndicator.style.cssText = `
        margin-top: 8px;
        padding: 6px 10px;
        background: #fef7e0;
        border-radius: 4px;
        font-size: 12px;
        color: #b06000;
        font-weight: 500;
      `
      stateIndicator.textContent = '⚠️ Manual Review Required'
      taskCard.appendChild(stateIndicator)
    } else if (task.state === TaskState.SchedulingConflict) {
      const stateIndicator = document.createElement('div')
      stateIndicator.style.cssText = `
        margin-top: 8px;
        padding: 6px 10px;
        background: #fce8e6;
        border-radius: 4px;
        font-size: 12px;
        color: #c5221f;
        font-weight: 500;
      `
      stateIndicator.textContent = '❌ Scheduling Conflict'
      taskCard.appendChild(stateIndicator)
    } else if (task.state === TaskState.Scheduled && task.calendarBlockId) {
      const stateIndicator = document.createElement('div')
      stateIndicator.style.cssText = `
        margin-top: 8px;
        padding: 6px 10px;
        background: #e6f4ea;
        border-radius: 4px;
        font-size: 12px;
        color: #137333;
        font-weight: 500;
      `
      stateIndicator.textContent = '✓ Scheduled on Calendar'
      taskCard.appendChild(stateIndicator)
    }

    container.appendChild(taskCard)
  }

  /**
   * Format deadline for display
   */
  private formatDeadline(deadline: string): string {
    try {
      const date = new Date(deadline)
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
      })
    } catch {
      return deadline
    }
  }

  /**
   * Format priority for display
   */
  private formatPriority(priority: Priority): string {
    const priorityMap: Record<Priority, string> = {
      [Priority.High]: '🔴 High',
      [Priority.Medium]: '🟡 Medium',
      [Priority.Low]: '🟢 Low',
    }
    return priorityMap[priority] || priority
  }

  /**
   * Render the feedback panel with execution statistics
   */
  renderFeedbackPanel(stats: FeedbackStats): void {
    // Get or create feedback panel container
    const panelId = `${this.containerId}-feedback`
    let panel = document.getElementById(panelId)
    
    if (!panel) {
      panel = document.createElement('div')
      panel.id = panelId
      panel.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 350px;
        background: white;
        border: 1px solid #dadce0;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        z-index: 10000;
        font-family: 'Google Sans', Roboto, Arial, sans-serif;
      `
      document.body.appendChild(panel)
    }

    // Clear existing content
    panel.innerHTML = ''

    // Add header
    const header = document.createElement('div')
    header.style.cssText = `
      padding: 16px;
      border-bottom: 1px solid #dadce0;
      font-size: 16px;
      font-weight: 500;
      color: #202124;
    `
    header.textContent = 'Execution Summary'
    panel.appendChild(header)

    // Add stats container
    const statsContainer = document.createElement('div')
    statsContainer.style.cssText = `
      padding: 16px;
    `

    // Create stat items
    const statItems = [
      {
        label: 'Tasks Extracted',
        value: stats.tasksExtracted,
        icon: '📋',
        color: '#1967d2',
      },
      {
        label: 'Calendar Blocks Created',
        value: stats.calendarBlocksCreated,
        icon: '📅',
        color: '#34a853',
      },
      {
        label: 'Scheduling Conflicts',
        value: stats.schedulingConflicts,
        icon: '⚠️',
        color: '#ea4335',
      },
      {
        label: 'Manual Review Items',
        value: stats.manualReviewItems,
        icon: '👁️',
        color: '#f9ab00',
      },
    ]

    statItems.forEach(item => {
      const statItem = document.createElement('div')
      statItem.style.cssText = `
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f1f3f4;
      `

      const labelContainer = document.createElement('div')
      labelContainer.style.cssText = `
        display: flex;
        align-items: center;
        gap: 8px;
      `

      const icon = document.createElement('span')
      icon.style.cssText = `
        font-size: 18px;
      `
      icon.textContent = item.icon

      const label = document.createElement('span')
      label.style.cssText = `
        font-size: 14px;
        color: #5f6368;
      `
      label.textContent = item.label

      labelContainer.appendChild(icon)
      labelContainer.appendChild(label)

      const value = document.createElement('span')
      value.style.cssText = `
        font-size: 18px;
        font-weight: 500;
        color: ${item.color};
      `
      value.textContent = item.value.toString()

      statItem.appendChild(labelContainer)
      statItem.appendChild(value)
      statsContainer.appendChild(statItem)
    })

    panel.appendChild(statsContainer)
  }

  /**
   * Render the execution log panel
   */
  renderExecutionLog(logs: LogEntry[]): void {
    // Get or create log panel container
    const panelId = `${this.containerId}-logs`
    let panel = document.getElementById(panelId)
    
    if (!panel) {
      panel = document.createElement('div')
      panel.id = panelId
      panel.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 20px;
        width: 450px;
        max-height: 400px;
        background: white;
        border: 1px solid #dadce0;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        z-index: 10000;
        font-family: 'Google Sans', Roboto, Arial, sans-serif;
        display: flex;
        flex-direction: column;
      `
      document.body.appendChild(panel)
    }

    // Clear existing content
    panel.innerHTML = ''

    // Add header
    const header = document.createElement('div')
    header.style.cssText = `
      padding: 16px;
      border-bottom: 1px solid #dadce0;
      font-size: 16px;
      font-weight: 500;
      color: #202124;
      flex-shrink: 0;
    `
    header.textContent = 'Execution Log'
    panel.appendChild(header)

    // Add logs container with scrolling
    const logsContainer = document.createElement('div')
    logsContainer.style.cssText = `
      padding: 12px 16px;
      overflow-y: auto;
      flex-grow: 1;
    `

    if (logs.length === 0) {
      const emptyState = document.createElement('div')
      emptyState.style.cssText = `
        padding: 20px;
        text-align: center;
        color: #5f6368;
        font-size: 14px;
      `
      emptyState.textContent = 'No log entries'
      logsContainer.appendChild(emptyState)
    } else {
      logs.forEach(log => {
        const logEntry = document.createElement('div')
        logEntry.style.cssText = `
          padding: 10px 0;
          border-bottom: 1px solid #f1f3f4;
          font-size: 13px;
        `

        // Timestamp
        const timestamp = document.createElement('div')
        timestamp.style.cssText = `
          font-size: 11px;
          color: #80868b;
          margin-bottom: 4px;
        `
        timestamp.textContent = this.formatLogTimestamp(log.timestamp)
        logEntry.appendChild(timestamp)

        // Message with level indicator
        const messageContainer = document.createElement('div')
        messageContainer.style.cssText = `
          display: flex;
          align-items: flex-start;
          gap: 8px;
        `

        // Level icon
        const levelIcon = document.createElement('span')
        levelIcon.style.cssText = `
          flex-shrink: 0;
          font-size: 14px;
        `
        
        let icon = ''
        let messageColor = '#202124'
        
        switch (log.level) {
          case 'error':
            icon = '❌'
            messageColor = '#d93025'
            break
          case 'warning':
            icon = '⚠️'
            messageColor = '#f9ab00'
            break
          case 'info':
          default:
            icon = 'ℹ️'
            messageColor = '#5f6368'
            break
        }
        
        levelIcon.textContent = icon
        messageContainer.appendChild(levelIcon)

        // Message text
        const message = document.createElement('span')
        message.style.cssText = `
          color: ${messageColor};
          line-height: 1.4;
          word-break: break-word;
        `
        message.textContent = log.message
        messageContainer.appendChild(message)

        logEntry.appendChild(messageContainer)
        logsContainer.appendChild(logEntry)
      })
    }

    panel.appendChild(logsContainer)
  }

  /**
   * Format log timestamp for display
   */
  private formatLogTimestamp(timestamp: string): string {
    try {
      const date = new Date(timestamp)
      return date.toLocaleString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
      })
    } catch {
      return timestamp
    }
  }

  /**
   * Group tasks by timeline (Today, Tomorrow, Upcoming)
   */
  groupTasksByTimeline(tasks: TaskDisplayData[]): TimelineGroups {
    const now = new Date()
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const todayEnd = new Date(todayStart)
    todayEnd.setDate(todayEnd.getDate() + 1)
    
    const tomorrowEnd = new Date(todayEnd)
    tomorrowEnd.setDate(tomorrowEnd.getDate() + 1)

    const today: TaskDisplayData[] = []
    const tomorrow: TaskDisplayData[] = []
    const upcoming: TaskDisplayData[] = []

    tasks.forEach(task => {
      try {
        const deadline = new Date(task.deadline)
        
        if (deadline >= todayStart && deadline < todayEnd) {
          today.push(task)
        } else if (deadline >= todayEnd && deadline < tomorrowEnd) {
          tomorrow.push(task)
        } else if (deadline >= tomorrowEnd) {
          upcoming.push(task)
        }
        // Tasks with past deadlines are not displayed in any group
      } catch (error) {
        // If deadline parsing fails, put in upcoming
        upcoming.push(task)
      }
    })

    return { today, tomorrow, upcoming }
  }
}

/**
 * Error display component for showing errors to users
 * Requirements: 16.3, 16.4
 */
export class ErrorDisplayRenderer {
  private containerId: string

  constructor(containerId: string = 'ai-agent-error-display') {
    this.containerId = containerId
  }

  /**
   * Display an error message to the user
   * Requirements: 16.3, 16.4
   */
  displayError(error: { code: string; message: string; context?: Record<string, unknown> }): void {
    // Get or create error display container
    let errorContainer = document.getElementById(this.containerId)

    if (!errorContainer) {
      errorContainer = document.createElement('div')
      errorContainer.id = this.containerId
      errorContainer.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        width: 400px;
        background: #fce8e6;
        border: 2px solid #ea4335;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 10001;
        font-family: 'Google Sans', Roboto, Arial, sans-serif;
        animation: slideIn 0.3s ease-out;
      `
      document.body.appendChild(errorContainer)
    }

    // Clear existing content
    errorContainer.innerHTML = ''

    // Add header
    const header = document.createElement('div')
    header.style.cssText = `
      padding: 16px;
      border-bottom: 1px solid #ea4335;
      font-size: 16px;
      font-weight: 500;
      color: #c5221f;
      display: flex;
      justify-content: space-between;
      align-items: center;
    `
    header.innerHTML = `
      <span>❌ Error</span>
      <button id="${this.containerId}-close-btn" style="
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
        color: #c5221f;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
      ">×</button>
    `
    errorContainer.appendChild(header)

    // Add error content
    const content = document.createElement('div')
    content.style.cssText = `
      padding: 16px;
    `

    // Error code
    const codeElement = document.createElement('div')
    codeElement.style.cssText = `
      font-size: 12px;
      color: #5f6368;
      margin-bottom: 8px;
      font-family: monospace;
    `
    codeElement.textContent = `Error Code: ${error.code}`
    content.appendChild(codeElement)

    // Error message
    const messageElement = document.createElement('div')
    messageElement.style.cssText = `
      font-size: 14px;
      color: #202124;
      line-height: 1.5;
      margin-bottom: 12px;
    `
    messageElement.textContent = error.message
    content.appendChild(messageElement)

    // Actionable guidance based on error code
    const guidance = this.getErrorGuidance(error.code)
    if (guidance) {
      const guidanceElement = document.createElement('div')
      guidanceElement.style.cssText = `
        font-size: 13px;
        color: #5f6368;
        padding: 12px;
        background: white;
        border-radius: 4px;
        border-left: 3px solid #f9ab00;
      `
      guidanceElement.innerHTML = `<strong>💡 Suggestion:</strong> ${guidance}`
      content.appendChild(guidanceElement)
    }

    errorContainer.appendChild(content)

    // Wire close button
    const closeBtn = document.getElementById(`${this.containerId}-close-btn`)
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        this.dismissError()
      })
    }

    // Auto-dismiss after 10 seconds
    setTimeout(() => {
      this.dismissError()
    }, 10000)
  }

  /**
   * Dismiss/remove the error display
   */
  dismissError(): void {
    const errorContainer = document.getElementById(this.containerId)
    if (errorContainer && errorContainer.parentNode) {
      errorContainer.remove()
    }
  }

  /**
   * Get actionable guidance for specific error codes
   * Requirements: 16.4
   */
  private getErrorGuidance(errorCode: string): string | null {
    const guidanceMap: Record<string, string> = {
      INITIALIZATION_ERROR: 'Try refreshing the Gmail page and ensure you are viewing an email.',
      TIMEOUT: 'The backend server is taking too long to respond. Please try again.',
      NETWORK_ERROR: 'Cannot connect to the backend server. Check your internet connection and ensure the backend is running.',
      HTTP_401: 'Authentication failed. Please check your API credentials.',
      HTTP_422: 'Invalid request data. Please ensure you have opened a valid email.',
      HTTP_500: 'Backend server error. Please try again later or contact support.',
      INVALID_RESPONSE: 'Received invalid response from backend. Please try again.',
      EXECUTION_ERROR: 'Please ensure you have opened an email before clicking "Run Agent".',
      UNKNOWN_ERROR: 'An unexpected error occurred. Please try again or contact support.',
    }

    return guidanceMap[errorCode] || null
  }
}

