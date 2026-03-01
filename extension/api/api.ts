/** API client for backend communication. */

import { EmailContent } from '../content/content'

// Export types
export interface RunAgentRequest {
  emailContent: EmailContent
  userTimezone: string
  calendarId: string
}

export interface RunAgentResponse {
  tasks: TaskDisplayData[]
  stats: FeedbackStats
  logs: LogEntry[]
  errors: ErrorDetail[]
}

export interface TaskDisplayData {
  id: string
  title: string
  description: string
  deadline: string
  owner: string
  confidence: number
  priority: string
  state: string
  calendarBlockId?: string
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
}

export interface ErrorDetail {
  code: string
  message: string
  context?: Record<string, unknown>
}

// Export API client class
export class BackendAPIClient {
  private readonly backendUrl: string
  private readonly timeoutMs: number

  constructor(backendUrl: string, timeoutMs: number = 30000) {
    // Enforce HTTPS
    if (!backendUrl.startsWith('https://')) {
      throw new Error('Backend URL must use HTTPS protocol')
    }
    this.backendUrl = backendUrl
    this.timeoutMs = timeoutMs
  }

  /**
   * Send a run-agent request to the backend
   */
  async runAgent(request: RunAgentRequest): Promise<RunAgentResponse> {
    try {
      // Create abort controller for timeout handling
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), this.timeoutMs)

      try {
        // Make POST request to /run-agent endpoint
        const response = await fetch(`${this.backendUrl}/run-agent`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request),
          signal: controller.signal,
        })

        clearTimeout(timeoutId)

        // Handle non-OK responses
        if (!response.ok) {
          const errorText = await response.text()
          let errorDetail: ErrorDetail
          
          try {
            const errorJson = JSON.parse(errorText)
            errorDetail = {
              code: `HTTP_${response.status}`,
              message: errorJson.message || errorJson.detail || response.statusText,
              context: errorJson,
            }
          } catch {
            errorDetail = {
              code: `HTTP_${response.status}`,
              message: response.statusText,
              context: { responseText: errorText },
            }
          }

          throw new BackendAPIError(
            `Backend request failed with status ${response.status}`,
            errorDetail
          )
        }

        // Parse and return structured response
        const data = await response.json()
        return this.validateResponse(data)
      } catch (error) {
        clearTimeout(timeoutId)
        throw error
      }
    } catch (error) {
      // Handle timeout errors
      if (error instanceof Error && error.name === 'AbortError') {
        throw new BackendAPIError('Request timeout', {
          code: 'TIMEOUT',
          message: `Request exceeded ${this.timeoutMs}ms timeout`,
        })
      }

      // Handle network errors
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new BackendAPIError('Network error', {
          code: 'NETWORK_ERROR',
          message: 'Failed to connect to backend server',
          context: { originalError: error.message },
        })
      }

      // Re-throw BackendAPIError as-is
      if (error instanceof BackendAPIError) {
        throw error
      }

      // Wrap other errors
      throw new BackendAPIError('Unexpected error', {
        code: 'UNKNOWN_ERROR',
        message: error instanceof Error ? error.message : String(error),
      })
    }
  }

  /**
   * Validate the response structure
   */
  private validateResponse(data: unknown): RunAgentResponse {
    if (!data || typeof data !== 'object') {
      throw new BackendAPIError('Invalid response format', {
        code: 'INVALID_RESPONSE',
        message: 'Response is not a valid object',
      })
    }

    const response = data as Partial<RunAgentResponse>

    // Validate required fields
    if (!Array.isArray(response.tasks)) {
      throw new BackendAPIError('Invalid response format', {
        code: 'INVALID_RESPONSE',
        message: 'Response missing tasks array',
      })
    }

    if (!response.stats || typeof response.stats !== 'object') {
      throw new BackendAPIError('Invalid response format', {
        code: 'INVALID_RESPONSE',
        message: 'Response missing stats object',
      })
    }

    if (!Array.isArray(response.logs)) {
      throw new BackendAPIError('Invalid response format', {
        code: 'INVALID_RESPONSE',
        message: 'Response missing logs array',
      })
    }

    if (!Array.isArray(response.errors)) {
      throw new BackendAPIError('Invalid response format', {
        code: 'INVALID_RESPONSE',
        message: 'Response missing errors array',
      })
    }

    return response as RunAgentResponse
  }
}

/**
 * Custom error class for backend API errors
 */
export class BackendAPIError extends Error {
  public readonly errorDetail: ErrorDetail

  constructor(message: string, errorDetail: ErrorDetail) {
    super(message)
    this.name = 'BackendAPIError'
    this.errorDetail = errorDetail
  }
}
