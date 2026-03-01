/** Task action handlers for user interactions. */

import { TaskDisplayData, TaskState } from '../ui/ui'

// Export action handler class
export class TaskActionHandler {
  private tasks: TaskDisplayData[]
  private onTasksUpdated?: (tasks: TaskDisplayData[]) => void

  constructor(tasks: TaskDisplayData[], onTasksUpdated?: (tasks: TaskDisplayData[]) => void) {
    this.tasks = tasks
    this.onTasksUpdated = onTasksUpdated
  }

  /**
   * Adjust the deadline for a task
   * Requirements: 9.1, 9.2
   */
  adjustDeadline(taskId: string, newDeadline: Date): void {
    const task = this.tasks.find(t => t.id === taskId)
    if (!task) {
      console.error(`Task with id ${taskId} not found`)
      return
    }

    // Update the task deadline
    task.deadline = newDeadline.toISOString()

    // Notify listeners that tasks have been updated
    if (this.onTasksUpdated) {
      this.onTasksUpdated(this.tasks)
    }

    console.log(`Deadline adjusted for task ${taskId} to ${newDeadline.toISOString()}`)
  }

  /**
   * Discard a task from the display
   * Requirements: 9.3, 9.4
   */
  discardTask(taskId: string): void {
    const taskIndex = this.tasks.findIndex(t => t.id === taskId)
    if (taskIndex === -1) {
      console.error(`Task with id ${taskId} not found`)
      return
    }

    // Mark task as discarded instead of removing it
    this.tasks[taskIndex].state = TaskState.Discarded

    // Remove the task from the array
    this.tasks.splice(taskIndex, 1)

    // Notify listeners that tasks have been updated
    if (this.onTasksUpdated) {
      this.onTasksUpdated(this.tasks)
    }

    console.log(`Task ${taskId} discarded`)
  }

  /**
   * Attach event listeners to task elements in the DOM
   * Requirements: 9.1, 9.3, 9.5, 9.6, 9.7
   */
  attachEventListeners(): void {
    // Find all task cards in the DOM
    const taskCards = document.querySelectorAll('[data-task-id]')

    taskCards.forEach(card => {
      const taskId = (card as HTMLElement).dataset.taskId
      if (!taskId) return

      // Add deadline adjustment button if not already present
      if (!card.querySelector('.deadline-adjust-btn')) {
        this.addDeadlineAdjustButton(card as HTMLElement, taskId)
      }

      // Add discard button if not already present
      if (!card.querySelector('.discard-btn')) {
        this.addDiscardButton(card as HTMLElement, taskId)
      }

      // Ensure title, description, and owner are not editable
      this.ensureReadOnly(card as HTMLElement)
    })
  }

  /**
   * Add deadline adjustment button to a task card
   */
  private addDeadlineAdjustButton(card: HTMLElement, taskId: string): void {
    const task = this.tasks.find(t => t.id === taskId)
    if (!task) return

    // Create action buttons container if it doesn't exist
    let actionsContainer = card.querySelector('.task-actions') as HTMLElement
    if (!actionsContainer) {
      actionsContainer = document.createElement('div')
      actionsContainer.className = 'task-actions'
      actionsContainer.style.cssText = `
        margin-top: 12px;
        display: flex;
        gap: 8px;
        align-items: center;
      `
      card.appendChild(actionsContainer)
    }

    // Create deadline adjustment button
    const adjustBtn = document.createElement('button')
    adjustBtn.className = 'deadline-adjust-btn'
    adjustBtn.style.cssText = `
      padding: 6px 12px;
      background: #1967d2;
      color: white;
      border: none;
      border-radius: 4px;
      font-size: 12px;
      cursor: pointer;
      font-family: 'Google Sans', Roboto, Arial, sans-serif;
      transition: background 0.2s;
    `
    adjustBtn.textContent = '📅 Adjust Deadline'
    adjustBtn.onmouseover = () => {
      adjustBtn.style.background = '#1557b0'
    }
    adjustBtn.onmouseout = () => {
      adjustBtn.style.background = '#1967d2'
    }

    // Add click event listener
    adjustBtn.addEventListener('click', (e) => {
      e.stopPropagation()
      this.showDeadlinePicker(taskId, task.deadline)
    })

    actionsContainer.appendChild(adjustBtn)
  }

  /**
   * Add discard button to a task card
   */
  private addDiscardButton(card: HTMLElement, taskId: string): void {
    // Create action buttons container if it doesn't exist
    let actionsContainer = card.querySelector('.task-actions') as HTMLElement
    if (!actionsContainer) {
      actionsContainer = document.createElement('div')
      actionsContainer.className = 'task-actions'
      actionsContainer.style.cssText = `
        margin-top: 12px;
        display: flex;
        gap: 8px;
        align-items: center;
      `
      card.appendChild(actionsContainer)
    }

    // Create discard button
    const discardBtn = document.createElement('button')
    discardBtn.className = 'discard-btn'
    discardBtn.style.cssText = `
      padding: 6px 12px;
      background: #ea4335;
      color: white;
      border: none;
      border-radius: 4px;
      font-size: 12px;
      cursor: pointer;
      font-family: 'Google Sans', Roboto, Arial, sans-serif;
      transition: background 0.2s;
    `
    discardBtn.textContent = '🗑️ Discard'
    discardBtn.onmouseover = () => {
      discardBtn.style.background = '#d33426'
    }
    discardBtn.onmouseout = () => {
      discardBtn.style.background = '#ea4335'
    }

    // Add click event listener
    discardBtn.addEventListener('click', (e) => {
      e.stopPropagation()
      if (confirm('Are you sure you want to discard this task?')) {
        this.discardTask(taskId)
        // Remove the card from DOM
        card.remove()
      }
    })

    actionsContainer.appendChild(discardBtn)
  }

  /**
   * Show date picker for deadline adjustment
   */
  private showDeadlinePicker(taskId: string, currentDeadline: string): void {
    // Create modal overlay
    const overlay = document.createElement('div')
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      z-index: 20000;
      display: flex;
      align-items: center;
      justify-content: center;
    `

    // Create modal content
    const modal = document.createElement('div')
    modal.style.cssText = `
      background: white;
      padding: 24px;
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      font-family: 'Google Sans', Roboto, Arial, sans-serif;
      min-width: 300px;
    `

    // Modal title
    const title = document.createElement('h3')
    title.style.cssText = `
      margin: 0 0 16px 0;
      font-size: 18px;
      color: #202124;
    `
    title.textContent = 'Adjust Deadline'
    modal.appendChild(title)

    // Date input
    const dateInput = document.createElement('input')
    dateInput.type = 'datetime-local'
    dateInput.style.cssText = `
      width: 100%;
      padding: 10px;
      border: 1px solid #dadce0;
      border-radius: 4px;
      font-size: 14px;
      margin-bottom: 16px;
      font-family: 'Google Sans', Roboto, Arial, sans-serif;
    `
    
    // Set current deadline as default value
    try {
      const currentDate = new Date(currentDeadline)
      // Format for datetime-local input (YYYY-MM-DDTHH:MM)
      const year = currentDate.getFullYear()
      const month = String(currentDate.getMonth() + 1).padStart(2, '0')
      const day = String(currentDate.getDate()).padStart(2, '0')
      const hours = String(currentDate.getHours()).padStart(2, '0')
      const minutes = String(currentDate.getMinutes()).padStart(2, '0')
      dateInput.value = `${year}-${month}-${day}T${hours}:${minutes}`
    } catch (error) {
      console.error('Error parsing current deadline:', error)
    }

    modal.appendChild(dateInput)

    // Buttons container
    const buttonsContainer = document.createElement('div')
    buttonsContainer.style.cssText = `
      display: flex;
      gap: 8px;
      justify-content: flex-end;
    `

    // Cancel button
    const cancelBtn = document.createElement('button')
    cancelBtn.style.cssText = `
      padding: 8px 16px;
      background: white;
      color: #1967d2;
      border: 1px solid #dadce0;
      border-radius: 4px;
      font-size: 14px;
      cursor: pointer;
      font-family: 'Google Sans', Roboto, Arial, sans-serif;
    `
    cancelBtn.textContent = 'Cancel'
    cancelBtn.addEventListener('click', () => {
      overlay.remove()
    })
    buttonsContainer.appendChild(cancelBtn)

    // Save button
    const saveBtn = document.createElement('button')
    saveBtn.style.cssText = `
      padding: 8px 16px;
      background: #1967d2;
      color: white;
      border: none;
      border-radius: 4px;
      font-size: 14px;
      cursor: pointer;
      font-family: 'Google Sans', Roboto, Arial, sans-serif;
    `
    saveBtn.textContent = 'Save'
    saveBtn.addEventListener('click', () => {
      if (dateInput.value) {
        const newDeadline = new Date(dateInput.value)
        this.adjustDeadline(taskId, newDeadline)
        overlay.remove()
      } else {
        alert('Please select a valid date and time')
      }
    })
    buttonsContainer.appendChild(saveBtn)

    modal.appendChild(buttonsContainer)
    overlay.appendChild(modal)
    document.body.appendChild(overlay)

    // Close on overlay click
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.remove()
      }
    })
  }

  /**
   * Ensure task fields are read-only (no editing of title/description/owner)
   * Requirements: 9.5, 9.6, 9.7
   */
  private ensureReadOnly(card: HTMLElement): void {
    // Find all text elements in the card
    const textElements = card.querySelectorAll('div')
    
    textElements.forEach(element => {
      // Ensure contentEditable is false
      if (element.hasAttribute('contenteditable')) {
        element.removeAttribute('contenteditable')
      }
      
      // Set contentEditable to false explicitly
      (element as HTMLElement).contentEditable = 'false'
      
      // Remove any input or textarea elements that might allow editing
      const inputs = element.querySelectorAll('input, textarea')
      inputs.forEach(input => {
        if (!input.classList.contains('deadline-adjust-input')) {
          input.remove()
        }
      })
    })

    // Ensure the card itself is not editable
    card.contentEditable = 'false'
    card.style.userSelect = 'text' // Allow text selection but not editing
  }

  /**
   * Export tasks to CSV
   */
  exportTasksToCSV(tasks: TaskDisplayData[]): void {
    // Requirements: 11.1, 11.2, 11.3
    if (tasks.length === 0) {
      console.warn('No tasks to export')
      return
    }

    // CSV header
    const headers = ['Title', 'Description', 'Deadline', 'Owner', 'Priority', 'Confidence']
    
    // Escape CSV field - handle quotes and commas
    const escapeCSVField = (field: string | number): string => {
      const str = String(field)
      // If field contains comma, quote, or newline, wrap in quotes and escape internal quotes
      if (str.includes(',') || str.includes('"') || str.includes('\n') || str.includes('\r')) {
        return `"${str.replace(/"/g, '""')}"`
      }
      return str
    }

    // Build CSV rows
    const rows = tasks.map(task => {
      return [
        escapeCSVField(task.title),
        escapeCSVField(task.description),
        escapeCSVField(task.deadline),
        escapeCSVField(task.owner),
        escapeCSVField(task.priority),
        escapeCSVField(task.confidence)
      ].join(',')
    })

    // Combine header and rows
    const csvContent = [headers.join(','), ...rows].join('\n')

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `tasks_export_${new Date().toISOString().split('T')[0]}.csv`
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    console.log(`Exported ${tasks.length} tasks to CSV`)
  }

  /**
   * Export meeting prep document to PDF
   * Requirements: 11.4, 11.5
   */
  exportMeetingPrepToPDF(prepDocument: MeetingPrepDocument): void {
    // Create a formatted HTML document for the meeting prep
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Meeting Prep: ${this.escapeHtml(prepDocument.meetingTitle)}</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 800px;
      margin: 40px auto;
      padding: 20px;
      line-height: 1.6;
      color: #333;
    }
    h1 {
      color: #2c3e50;
      border-bottom: 3px solid #3498db;
      padding-bottom: 10px;
      margin-bottom: 20px;
    }
    h2 {
      color: #34495e;
      margin-top: 30px;
      margin-bottom: 15px;
      border-left: 4px solid #3498db;
      padding-left: 10px;
    }
    .meeting-time {
      color: #7f8c8d;
      font-size: 14px;
      margin-bottom: 30px;
    }
    .section {
      margin-bottom: 25px;
    }
    .context-summary {
      background-color: #ecf0f1;
      padding: 15px;
      border-radius: 5px;
      margin-bottom: 20px;
    }
    ul {
      list-style-type: disc;
      padding-left: 25px;
    }
    li {
      margin-bottom: 8px;
    }
    @media print {
      body {
        margin: 0;
        padding: 20px;
      }
    }
  </style>
</head>
<body>
  <h1>${this.escapeHtml(prepDocument.meetingTitle)}</h1>
  <div class="meeting-time">Meeting Time: ${this.escapeHtml(prepDocument.meetingTime)}</div>
  
  <div class="section">
    <h2>Context Summary</h2>
    <div class="context-summary">
      ${this.escapeHtml(prepDocument.contextSummary)}
    </div>
  </div>
  
  <div class="section">
    <h2>Key Talking Points</h2>
    <ul>
      ${prepDocument.talkingPoints.map(point => `<li>${this.escapeHtml(point)}</li>`).join('\n      ')}
    </ul>
  </div>
  
  <div class="section">
    <h2>Questions to Ask</h2>
    <ul>
      ${prepDocument.questions.map(q => `<li>${this.escapeHtml(q)}</li>`).join('\n      ')}
    </ul>
  </div>
  
  <div class="section">
    <h2>Potential Risks or Concerns</h2>
    <ul>
      ${prepDocument.risks.map(risk => `<li>${this.escapeHtml(risk)}</li>`).join('\n      ')}
    </ul>
  </div>
</body>
</html>
    `

    // Create a blob and open in new window for printing
    const blob = new Blob([htmlContent], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const printWindow = window.open(url, '_blank')
    
    if (printWindow) {
      // Wait for content to load, then trigger print dialog
      printWindow.addEventListener('load', () => {
        setTimeout(() => {
          printWindow.print()
          // Clean up after a delay to allow print dialog to open
          setTimeout(() => {
            URL.revokeObjectURL(url)
          }, 1000)
        }, 500)
      })
    } else {
      console.error('Failed to open print window - popup may be blocked')
      URL.revokeObjectURL(url)
    }

    console.log(`Exported meeting prep document: ${prepDocument.meetingTitle}`)
  }

  /**
   * Escape HTML special characters to prevent XSS
   */
  private escapeHtml(text: string): string {
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
  }
}

export interface MeetingPrepDocument {
  meetingTitle: string
  meetingTime: string
  contextSummary: string
  talkingPoints: string[]
  questions: string[]
  risks: string[]
}
