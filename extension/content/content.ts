/** Content script for Gmail DOM extraction and UI rendering. */

// Export types
export interface EmailContent {
  subject: string
  body: string
  sender: string
  timestamp: string
  threadMessages: ThreadMessage[]
  forwardedMessages: ForwardedMessage[]
}

export interface ThreadMessage {
  sender: string
  timestamp: string
  body: string
}

export interface ForwardedMessage {
  originalSender: string
  originalTimestamp: string
  body: string
}

// Export DOM extractor class
export class GmailDOMExtractor {
  private buttonInjected = false

  /**
   * Inject the "Run Agent" button into the Gmail UI
   */
  injectRunAgentButton(): void {
    if (this.buttonInjected) {
      return
    }

    try {
      // Create the "Run Agent" button with fixed positioning
      const button = document.createElement('button')
      button.id = 'ai-agent-run-button'
      button.className = 'ai-execution-agent-button'
      button.textContent = 'Run AI Agent'
      button.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 12px 24px;
        background-color: #1a73e8;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 500;
      `

      // Add hover effect
      button.addEventListener('mouseenter', () => {
        button.style.backgroundColor = '#1557b0'
      })
      button.addEventListener('mouseleave', () => {
        button.style.backgroundColor = '#1a73e8'
      })

      // Append button to body (using fixed positioning)
      document.body.appendChild(button)
      this.buttonInjected = true
      console.log('AI Execution Agent button injected successfully')
    } catch (error) {
      console.error('Error injecting Run Agent button:', error)
    }
  }

  /**
   * Extract email content from the current Gmail page
   */
  extractEmailContent(): EmailContent {
    try {
      const subject = this.extractSubject()
      const body = this.extractBody()
      const sender = this.extractSender()
      const timestamp = this.extractTimestamp()
      const threadMessages = this.extractThreadMessages()
      const forwardedMessages = this.extractForwardedMessages()

      return {
        subject,
        body,
        sender,
        timestamp,
        threadMessages,
        forwardedMessages,
      }
    } catch (error) {
      console.error('Error extracting email content:', error)
      throw new Error('Failed to extract email content from Gmail DOM')
    }
  }

  /**
   * Extract email subject from Gmail DOM
   */
  private extractSubject(): string {
    try {
      // Gmail subject selectors (multiple fallbacks)
      const subjectElement = 
        document.querySelector('.hP') || // Standard subject line
        document.querySelector('[data-legacy-thread-id] h2') ||
        document.querySelector('.ha h2') ||
        document.querySelector('[role="heading"]')

      if (!subjectElement) {
        throw new Error('Subject element not found')
      }

      return subjectElement.textContent?.trim() || ''
    } catch (error) {
      console.error('Error extracting subject:', error)
      return ''
    }
  }

  /**
   * Extract email body from Gmail DOM
   */
  private extractBody(): string {
    try {
      // Gmail body selectors
      const bodyElements = document.querySelectorAll('.a3s.aiL') || // Message body
                          document.querySelectorAll('.ii.gt') ||
                          document.querySelectorAll('[data-message-id] .a3s')

      if (bodyElements.length === 0) {
        throw new Error('Body elements not found')
      }

      // Get the last message body (most recent in thread)
      const lastBody = bodyElements[bodyElements.length - 1]
      return lastBody?.textContent?.trim() || ''
    } catch (error) {
      console.error('Error extracting body:', error)
      return ''
    }
  }

  /**
   * Extract sender information from Gmail DOM
   */
  private extractSender(): string {
    try {
      // Gmail sender selectors
      const senderElement = 
        document.querySelector('.gD') || // Sender name/email
        document.querySelector('[email]') ||
        document.querySelector('.go')

      if (!senderElement) {
        throw new Error('Sender element not found')
      }

      // Try to get email attribute first, fallback to text content
      const email = senderElement.getAttribute('email') || 
                   senderElement.getAttribute('data-hovercard-id') ||
                   senderElement.textContent?.trim() || ''

      return email
    } catch (error) {
      console.error('Error extracting sender:', error)
      return ''
    }
  }

  /**
   * Extract timestamp from Gmail DOM
   */
  private extractTimestamp(): string {
    try {
      // Gmail timestamp selectors
      const timestampElement = 
        document.querySelector('.g3') || // Timestamp span
        document.querySelector('[data-tooltip]') ||
        document.querySelector('.gH span[title]')

      if (!timestampElement) {
        throw new Error('Timestamp element not found')
      }

      // Try to get title attribute (full timestamp) or text content
      const timestamp = timestampElement.getAttribute('title') || 
                       timestampElement.textContent?.trim() || ''

      return timestamp
    } catch (error) {
      console.error('Error extracting timestamp:', error)
      return new Date().toISOString()
    }
  }

  /**
   * Extract all messages from an email thread
   */
  extractThreadMessages(): ThreadMessage[] {
    try {
      const messages: ThreadMessage[] = []
      
      // Find all message containers in the thread
      const messageContainers = document.querySelectorAll('.adn.ads') || // Thread messages
                               document.querySelectorAll('[data-message-id]') ||
                               document.querySelectorAll('.gs')

      messageContainers.forEach((container) => {
        try {
          // Extract sender from this message
          const senderEl = container.querySelector('.gD') || 
                          container.querySelector('[email]')
          const sender = senderEl?.getAttribute('email') || 
                        senderEl?.textContent?.trim() || ''

          // Extract timestamp from this message
          const timestampEl = container.querySelector('.g3') ||
                             container.querySelector('[data-tooltip]')
          const timestamp = timestampEl?.getAttribute('title') || 
                           timestampEl?.textContent?.trim() || ''

          // Extract body from this message
          const bodyEl = container.querySelector('.a3s.aiL') ||
                        container.querySelector('.ii.gt')
          const body = bodyEl?.textContent?.trim() || ''

          // Only add if we have at least some content
          if (sender || body) {
            messages.push({ sender, timestamp, body })
          }
        } catch (error) {
          console.warn('Error extracting thread message:', error)
        }
      })

      return messages
    } catch (error) {
      console.error('Error extracting thread messages:', error)
      return []
    }
  }

  /**
   * Extract content from forwarded messages
   */
  extractForwardedMessages(): ForwardedMessage[] {
    try {
      const forwardedMessages: ForwardedMessage[] = []

      // Find forwarded message sections
      // Gmail typically marks forwarded content with specific classes or patterns
      const bodyElements = document.querySelectorAll('.a3s.aiL, .ii.gt')

      bodyElements.forEach((bodyEl) => {
        const bodyText = bodyEl.textContent || ''

        // Look for forwarded message patterns
        const forwardedPattern = /---------- Forwarded message ---------\s*From:\s*([^\n]+)\s*Date:\s*([^\n]+)/gi
        const matches = bodyText.matchAll(forwardedPattern)

        for (const match of matches) {
          try {
            const originalSender = match[1]?.trim() || ''
            const originalTimestamp = match[2]?.trim() || ''

            // Extract the forwarded body (text after the header until next forward or end)
            const headerIndex = bodyText.indexOf(match[0])
            const nextForwardIndex = bodyText.indexOf('---------- Forwarded message', headerIndex + match[0].length)
            const bodyEndIndex = nextForwardIndex > 0 ? nextForwardIndex : bodyText.length
            const body = bodyText.substring(headerIndex + match[0].length, bodyEndIndex).trim()

            if (originalSender || body) {
              forwardedMessages.push({
                originalSender,
                originalTimestamp,
                body,
              })
            }
          } catch (error) {
            console.warn('Error parsing forwarded message:', error)
          }
        }

        // Also check for alternative forwarded message format
        const altPattern = /Begin forwarded message:\s*From:\s*([^\n]+)\s*Date:\s*([^\n]+)/gi
        const altMatches = bodyText.matchAll(altPattern)

        for (const match of altMatches) {
          try {
            const originalSender = match[1]?.trim() || ''
            const originalTimestamp = match[2]?.trim() || ''

            const headerIndex = bodyText.indexOf(match[0])
            const nextForwardIndex = bodyText.indexOf('Begin forwarded message:', headerIndex + match[0].length)
            const bodyEndIndex = nextForwardIndex > 0 ? nextForwardIndex : bodyText.length
            const body = bodyText.substring(headerIndex + match[0].length, bodyEndIndex).trim()

            if (originalSender || body) {
              forwardedMessages.push({
                originalSender,
                originalTimestamp,
                body,
              })
            }
          } catch (error) {
            console.warn('Error parsing alternative forwarded message:', error)
          }
        }
      })

      return forwardedMessages
    } catch (error) {
      console.error('Error extracting forwarded messages:', error)
      return []
    }
  }
}
