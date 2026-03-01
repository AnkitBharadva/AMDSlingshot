/**
 * Property-based tests for Gmail DOM extraction
 * Feature: ai-execution-agent
 */

import { describe, it, expect, beforeEach } from 'vitest'
import fc from 'fast-check'
import { GmailDOMExtractor } from './content'

// Helper to create mock Gmail DOM structure
function createMockGmailDOM(config: {
  subject: string
  body: string
  sender: string
  timestamp: string
  senderEmail?: string
}): void {
  // Clear existing DOM
  document.body.innerHTML = ''

  // Create Gmail-like structure
  const container = document.createElement('div')
  
  // Subject
  const subjectEl = document.createElement('h2')
  subjectEl.className = 'hP'
  subjectEl.textContent = config.subject
  container.appendChild(subjectEl)

  // Sender
  const senderEl = document.createElement('span')
  senderEl.className = 'gD'
  senderEl.textContent = config.sender
  if (config.senderEmail) {
    senderEl.setAttribute('email', config.senderEmail)
  }
  container.appendChild(senderEl)

  // Timestamp
  const timestampEl = document.createElement('span')
  timestampEl.className = 'g3'
  timestampEl.setAttribute('title', config.timestamp)
  timestampEl.textContent = config.timestamp
  container.appendChild(timestampEl)

  // Body
  const bodyEl = document.createElement('div')
  bodyEl.className = 'a3s aiL'
  bodyEl.textContent = config.body
  container.appendChild(bodyEl)

  document.body.appendChild(container)
}

// Helper to create mock Gmail DOM with thread messages
function createMockGmailThreadDOM(messages: Array<{
  sender: string
  senderEmail?: string
  timestamp: string
  body: string
}>): void {
  document.body.innerHTML = ''

  const container = document.createElement('div')

  messages.forEach((msg) => {
    const messageContainer = document.createElement('div')
    messageContainer.className = 'adn ads'
    messageContainer.setAttribute('data-message-id', `msg-${Math.random()}`)

    // Sender
    const senderEl = document.createElement('span')
    senderEl.className = 'gD'
    senderEl.textContent = msg.sender
    if (msg.senderEmail) {
      senderEl.setAttribute('email', msg.senderEmail)
    }
    messageContainer.appendChild(senderEl)

    // Timestamp
    const timestampEl = document.createElement('span')
    timestampEl.className = 'g3'
    timestampEl.setAttribute('title', msg.timestamp)
    timestampEl.textContent = msg.timestamp
    messageContainer.appendChild(timestampEl)

    // Body
    const bodyEl = document.createElement('div')
    bodyEl.className = 'a3s aiL'
    bodyEl.textContent = msg.body
    messageContainer.appendChild(bodyEl)

    container.appendChild(messageContainer)
  })

  document.body.appendChild(container)
}

// Helper to create mock Gmail DOM with forwarded messages
function createMockGmailForwardedDOM(forwardedContent: string): void {
  document.body.innerHTML = ''

  const container = document.createElement('div')
  const bodyEl = document.createElement('div')
  bodyEl.className = 'a3s aiL'
  bodyEl.textContent = forwardedContent
  container.appendChild(bodyEl)

  document.body.appendChild(container)
}

describe('GmailDOMExtractor - Property Tests', () => {
  let extractor: GmailDOMExtractor

  beforeEach(() => {
    extractor = new GmailDOMExtractor()
    document.body.innerHTML = ''
  })

  // Feature: ai-execution-agent, Property 1: Complete Email Field Extraction
  describe('Property 1: Complete Email Field Extraction', () => {
    it('should extract all required fields (subject, body, sender, timestamp) for any valid Gmail DOM', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 200 }).filter(s => s.trim().length > 0), // subject - exclude whitespace-only
          fc.string({ minLength: 1, maxLength: 1000 }).filter(s => s.trim().length > 0), // body - exclude whitespace-only
          fc.string({ minLength: 1, maxLength: 100 }).filter(s => s.trim().length > 0), // sender - exclude whitespace-only
          fc.emailAddress(), // senderEmail
          fc.date({ min: new Date('2020-01-01'), max: new Date('2030-12-31') }), // timestamp
          (subject, body, sender, senderEmail, timestamp) => {
            // Arrange: Create mock Gmail DOM
            createMockGmailDOM({
              subject,
              body,
              sender,
              senderEmail,
              timestamp: timestamp.toISOString(),
            })

            // Act: Extract email content
            const result = extractor.extractEmailContent()

            // Assert: All required fields should be extracted and non-empty
            // Note: Implementation trims whitespace, so compare against trimmed values
            expect(result.subject).toBeTruthy()
            expect(result.subject).toBe(subject.trim())
            
            expect(result.body).toBeTruthy()
            expect(result.body).toBe(body.trim())
            
            expect(result.sender).toBeTruthy()
            expect(result.sender).toBe(senderEmail)
            
            expect(result.timestamp).toBeTruthy()
            expect(result.timestamp).toBe(timestamp.toISOString())
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  // Feature: ai-execution-agent, Property 2: Thread Message Extraction Completeness
  describe('Property 2: Thread Message Extraction Completeness', () => {
    it('should extract exactly N thread messages for any email thread with N messages', () => {
      fc.assert(
        fc.property(
          fc.array(
            fc.record({
              sender: fc.string({ minLength: 1, maxLength: 100 }).filter(s => s.trim().length > 0),
              senderEmail: fc.emailAddress(),
              timestamp: fc.date({ min: new Date('2020-01-01'), max: new Date('2030-12-31') }),
              body: fc.string({ minLength: 1, maxLength: 500 }).filter(s => s.trim().length > 0),
            }),
            { minLength: 1, maxLength: 10 }
          ),
          (messages) => {
            // Arrange: Create mock Gmail thread DOM with N messages
            const mockMessages = messages.map((msg) => ({
              sender: msg.sender,
              senderEmail: msg.senderEmail,
              timestamp: msg.timestamp.toISOString(),
              body: msg.body,
            }))
            createMockGmailThreadDOM(mockMessages)

            // Act: Extract thread messages
            const result = extractor.extractThreadMessages()

            // Assert: Should extract exactly N messages
            expect(result).toHaveLength(messages.length)

            // Assert: Each message should have complete data
            // Note: Implementation trims whitespace, so compare against trimmed values
            result.forEach((threadMsg, index) => {
              expect(threadMsg.sender).toBeTruthy()
              expect(threadMsg.sender).toBe(mockMessages[index].senderEmail)
              expect(threadMsg.timestamp).toBeTruthy()
              expect(threadMsg.timestamp).toBe(mockMessages[index].timestamp)
              expect(threadMsg.body).toBeTruthy()
              expect(threadMsg.body).toBe(mockMessages[index].body.trim())
            })
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  // Feature: ai-execution-agent, Property 3: Forwarded Message Extraction
  describe('Property 3: Forwarded Message Extraction', () => {
    it('should extract all forwarded message sections with original sender, timestamp, and body', () => {
      fc.assert(
        fc.property(
          fc.array(
            fc.record({
              originalSender: fc.string({ minLength: 1, maxLength: 100 }).filter(s => s.trim().length > 0),
              originalTimestamp: fc.string({ minLength: 1, maxLength: 100 }).filter(s => s.trim().length > 0),
              body: fc.string({ minLength: 1, maxLength: 500 }).filter(s => s.trim().length > 0),
            }),
            { minLength: 1, maxLength: 5 }
          ),
          (forwardedMessages) => {
            // Arrange: Create forwarded message content
            const forwardedContent = forwardedMessages
              .map((msg) => {
                return `---------- Forwarded message ---------\nFrom: ${msg.originalSender}\nDate: ${msg.originalTimestamp}\n\n${msg.body}\n\n`
              })
              .join('\n')

            createMockGmailForwardedDOM(forwardedContent)

            // Act: Extract forwarded messages
            const result = extractor.extractForwardedMessages()

            // Assert: Should extract all forwarded messages
            expect(result).toHaveLength(forwardedMessages.length)

            // Assert: Each forwarded message should have complete data
            result.forEach((fwdMsg, index) => {
              expect(fwdMsg.originalSender).toBeTruthy()
              expect(fwdMsg.originalSender).toBe(forwardedMessages[index].originalSender.trim())
              expect(fwdMsg.originalTimestamp).toBeTruthy()
              expect(fwdMsg.originalTimestamp).toBe(forwardedMessages[index].originalTimestamp.trim())
              expect(fwdMsg.body).toBeTruthy()
              // Body should contain the original body content (trimmed)
              expect(fwdMsg.body.trim()).toContain(forwardedMessages[index].body.trim())
            })
          }
        ),
        { numRuns: 100 }
      )
    })
  })
})


describe('GmailDOMExtractor - Unit Tests', () => {
  let extractor: GmailDOMExtractor

  beforeEach(() => {
    extractor = new GmailDOMExtractor()
    document.body.innerHTML = ''
  })

  describe('extractEmailContent', () => {
    it('should extract content from standard Gmail structure', () => {
      // Arrange
      createMockGmailDOM({
        subject: 'Test Subject',
        body: 'Test body content',
        sender: 'John Doe',
        senderEmail: 'john@example.com',
        timestamp: '2024-01-15T10:30:00.000Z',
      })

      // Act
      const result = extractor.extractEmailContent()

      // Assert
      expect(result.subject).toBe('Test Subject')
      expect(result.body).toBe('Test body content')
      expect(result.sender).toBe('john@example.com')
      expect(result.timestamp).toBe('2024-01-15T10:30:00.000Z')
    })

    it('should handle empty email gracefully', () => {
      // Arrange - create minimal DOM structure
      document.body.innerHTML = '<div></div>'

      // Act
      const result = extractor.extractEmailContent()

      // Assert - should return empty strings but not throw
      expect(result.subject).toBe('')
      expect(result.body).toBe('')
      expect(result.sender).toBe('')
      expect(result.timestamp).toBeTruthy() // Falls back to current time
    })

    it('should handle malformed HTML structure', () => {
      // Arrange - create incomplete DOM structure
      const container = document.createElement('div')
      const subjectEl = document.createElement('h2')
      subjectEl.className = 'hP'
      subjectEl.textContent = 'Subject Only'
      container.appendChild(subjectEl)
      document.body.appendChild(container)

      // Act
      const result = extractor.extractEmailContent()

      // Assert - should extract what's available
      expect(result.subject).toBe('Subject Only')
      expect(result.body).toBe('')
      expect(result.sender).toBe('')
    })
  })

  describe('extractThreadMessages', () => {
    it('should extract multiple thread messages', () => {
      // Arrange
      createMockGmailThreadDOM([
        {
          sender: 'Alice',
          senderEmail: 'alice@example.com',
          timestamp: '2024-01-15T10:00:00.000Z',
          body: 'First message',
        },
        {
          sender: 'Bob',
          senderEmail: 'bob@example.com',
          timestamp: '2024-01-15T11:00:00.000Z',
          body: 'Second message',
        },
        {
          sender: 'Charlie',
          senderEmail: 'charlie@example.com',
          timestamp: '2024-01-15T12:00:00.000Z',
          body: 'Third message',
        },
      ])

      // Act
      const result = extractor.extractThreadMessages()

      // Assert
      expect(result).toHaveLength(3)
      expect(result[0].sender).toBe('alice@example.com')
      expect(result[0].body).toBe('First message')
      expect(result[1].sender).toBe('bob@example.com')
      expect(result[1].body).toBe('Second message')
      expect(result[2].sender).toBe('charlie@example.com')
      expect(result[2].body).toBe('Third message')
    })

    it('should return empty array when no thread messages exist', () => {
      // Arrange
      document.body.innerHTML = '<div></div>'

      // Act
      const result = extractor.extractThreadMessages()

      // Assert
      expect(result).toEqual([])
    })

    it('should handle malformed thread message structure', () => {
      // Arrange - create thread with incomplete data
      const container = document.createElement('div')
      const messageContainer = document.createElement('div')
      messageContainer.className = 'adn ads'
      
      const bodyEl = document.createElement('div')
      bodyEl.className = 'a3s aiL'
      bodyEl.textContent = 'Body only, no sender'
      messageContainer.appendChild(bodyEl)
      
      container.appendChild(messageContainer)
      document.body.appendChild(container)

      // Act
      const result = extractor.extractThreadMessages()

      // Assert - should still extract the message with available data
      expect(result).toHaveLength(1)
      expect(result[0].body).toBe('Body only, no sender')
      expect(result[0].sender).toBe('')
    })
  })

  describe('extractForwardedMessages', () => {
    it('should extract single forwarded message', () => {
      // Arrange
      const forwardedContent = `
Some intro text

---------- Forwarded message ---------
From: original@example.com
Date: Mon, Jan 15, 2024 at 10:00 AM

This is the forwarded message body.
It can span multiple lines.
      `
      createMockGmailForwardedDOM(forwardedContent)

      // Act
      const result = extractor.extractForwardedMessages()

      // Assert
      expect(result).toHaveLength(1)
      expect(result[0].originalSender).toBe('original@example.com')
      expect(result[0].originalTimestamp).toBe('Mon, Jan 15, 2024 at 10:00 AM')
      expect(result[0].body).toContain('This is the forwarded message body')
    })

    it('should extract multiple forwarded messages', () => {
      // Arrange
      const forwardedContent = `
---------- Forwarded message ---------
From: first@example.com
Date: Mon, Jan 15, 2024 at 10:00 AM

First forwarded message.

---------- Forwarded message ---------
From: second@example.com
Date: Mon, Jan 15, 2024 at 11:00 AM

Second forwarded message.
      `
      createMockGmailForwardedDOM(forwardedContent)

      // Act
      const result = extractor.extractForwardedMessages()

      // Assert
      expect(result).toHaveLength(2)
      expect(result[0].originalSender).toBe('first@example.com')
      expect(result[1].originalSender).toBe('second@example.com')
    })

    it('should handle alternative forwarded message format', () => {
      // Arrange
      const forwardedContent = `
Begin forwarded message:
From: alternative@example.com
Date: Tue, Jan 16, 2024 at 2:00 PM

Alternative format forwarded message.
      `
      createMockGmailForwardedDOM(forwardedContent)

      // Act
      const result = extractor.extractForwardedMessages()

      // Assert
      expect(result).toHaveLength(1)
      expect(result[0].originalSender).toBe('alternative@example.com')
      expect(result[0].originalTimestamp).toBe('Tue, Jan 16, 2024 at 2:00 PM')
    })

    it('should return empty array when no forwarded messages exist', () => {
      // Arrange
      createMockGmailForwardedDOM('Regular email content without forwarded messages')

      // Act
      const result = extractor.extractForwardedMessages()

      // Assert
      expect(result).toEqual([])
    })
  })

  describe('injectRunAgentButton', () => {
    it('should inject button into Gmail toolbar', () => {
      // Arrange - create mock Gmail toolbar
      const toolbar = document.createElement('div')
      toolbar.className = 'G-atb'
      document.body.appendChild(toolbar)

      // Act
      extractor.injectRunAgentButton()

      // Assert
      const button = document.getElementById('ai-agent-run-button')
      expect(button).toBeTruthy()
      expect(button?.textContent).toBe('Run Agent')
    })

    it('should not inject button twice', () => {
      // Arrange
      const toolbar = document.createElement('div')
      toolbar.className = 'G-atb'
      document.body.appendChild(toolbar)

      // Act
      extractor.injectRunAgentButton()
      extractor.injectRunAgentButton()

      // Assert - should only have one button
      const buttons = document.querySelectorAll('#ai-agent-run-button')
      expect(buttons).toHaveLength(1)
    })

    it('should handle missing toolbar gracefully', () => {
      // Arrange - no toolbar in DOM
      document.body.innerHTML = ''

      // Act & Assert - should not throw
      expect(() => extractor.injectRunAgentButton()).not.toThrow()
    })
  })
})
