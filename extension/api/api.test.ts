/** Unit tests for BackendAPIClient */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { BackendAPIClient, BackendAPIError, RunAgentRequest, RunAgentResponse } from './api'

describe('BackendAPIClient', () => {
  let client: BackendAPIClient
  const mockBackendUrl = 'https://api.example.com'
  
  // Mock fetch globally
  const originalFetch = global.fetch
  
  beforeEach(() => {
    client = new BackendAPIClient(mockBackendUrl, 5000)
  })
  
  afterEach(() => {
    global.fetch = originalFetch
    vi.clearAllMocks()
  })

  describe('constructor', () => {
    it('should enforce HTTPS protocol', () => {
      expect(() => new BackendAPIClient('http://api.example.com')).toThrow(
        'Backend URL must use HTTPS protocol'
      )
    })

    it('should accept HTTPS URLs', () => {
      expect(() => new BackendAPIClient('https://api.example.com')).not.toThrow()
    })

    it('should use default timeout if not provided', () => {
      const defaultClient = new BackendAPIClient('https://api.example.com')
      expect(defaultClient).toBeDefined()
    })
  })

  describe('runAgent', () => {
    const mockRequest: RunAgentRequest = {
      emailContent: {
        subject: 'Test Subject',
        body: 'Test Body',
        sender: 'test@example.com',
        timestamp: '2024-01-01T00:00:00Z',
        threadMessages: [],
        forwardedMessages: [],
      },
      userTimezone: 'UTC',
      calendarId: 'primary',
    }

    const mockResponse: RunAgentResponse = {
      tasks: [
        {
          id: '1',
          title: 'Test Task',
          description: 'Test Description',
          deadline: '2024-01-02T00:00:00Z',
          owner: 'test@example.com',
          confidence: 0.9,
          priority: 'high',
          state: 'scheduled',
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
          timestamp: '2024-01-01T00:00:00Z',
          message: 'Task extracted',
        },
      ],
      errors: [],
    }

    it('should successfully make a request and parse response', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      })

      const result = await client.runAgent(mockRequest)

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBackendUrl}/run-agent`,
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(mockRequest),
        })
      )

      expect(result).toEqual(mockResponse)
    })

    it('should handle network failures', async () => {
      global.fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'))

      await expect(client.runAgent(mockRequest)).rejects.toThrow(BackendAPIError)
      
      try {
        await client.runAgent(mockRequest)
      } catch (error) {
        expect(error).toBeInstanceOf(BackendAPIError)
        expect((error as BackendAPIError).errorDetail.code).toBe('NETWORK_ERROR')
        expect((error as BackendAPIError).errorDetail.message).toBe('Failed to connect to backend server')
      }
    })

    it('should handle timeout', async () => {
      // Create a client with very short timeout
      const shortTimeoutClient = new BackendAPIClient(mockBackendUrl, 100)
      
      global.fetch = vi.fn().mockImplementation((_url, options) => {
        return new Promise((_resolve, reject) => {
          // Simulate abort signal behavior
          if (options?.signal) {
            const signal = options.signal as AbortSignal
            const abortHandler = () => {
              const abortError = new Error('The operation was aborted')
              abortError.name = 'AbortError'
              reject(abortError)
            }
            signal.addEventListener('abort', abortHandler)
          }
          // Never resolve to simulate long request
        })
      })

      await expect(shortTimeoutClient.runAgent(mockRequest)).rejects.toThrow(BackendAPIError)
      
      try {
        await shortTimeoutClient.runAgent(mockRequest)
      } catch (error) {
        expect(error).toBeInstanceOf(BackendAPIError)
        expect((error as BackendAPIError).errorDetail.code).toBe('TIMEOUT')
        expect((error as BackendAPIError).errorDetail.message).toContain('timeout')
      }
    })

    it('should handle HTTP error responses with JSON error details', async () => {
      const errorResponse = {
        detail: 'Validation error',
        message: 'Invalid request format',
      }

      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        statusText: 'Unprocessable Entity',
        text: async () => JSON.stringify(errorResponse),
      })

      await expect(client.runAgent(mockRequest)).rejects.toThrow(BackendAPIError)
      
      try {
        await client.runAgent(mockRequest)
      } catch (error) {
        expect(error).toBeInstanceOf(BackendAPIError)
        expect((error as BackendAPIError).errorDetail.code).toBe('HTTP_422')
        expect((error as BackendAPIError).errorDetail.message).toBe('Invalid request format')
      }
    })

    it('should handle HTTP error responses with plain text', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => 'Server error occurred',
      })

      await expect(client.runAgent(mockRequest)).rejects.toThrow(BackendAPIError)
      
      try {
        await client.runAgent(mockRequest)
      } catch (error) {
        expect(error).toBeInstanceOf(BackendAPIError)
        expect((error as BackendAPIError).errorDetail.code).toBe('HTTP_500')
        expect((error as BackendAPIError).errorDetail.message).toBe('Internal Server Error')
      }
    })

    it('should validate response structure - missing tasks', async () => {
      const invalidResponse = {
        stats: mockResponse.stats,
        logs: mockResponse.logs,
        errors: mockResponse.errors,
      }

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => invalidResponse,
      })

      await expect(client.runAgent(mockRequest)).rejects.toThrow(BackendAPIError)
      
      try {
        await client.runAgent(mockRequest)
      } catch (error) {
        expect(error).toBeInstanceOf(BackendAPIError)
        expect((error as BackendAPIError).errorDetail.code).toBe('INVALID_RESPONSE')
        expect((error as BackendAPIError).errorDetail.message).toContain('tasks')
      }
    })

    it('should validate response structure - missing stats', async () => {
      const invalidResponse = {
        tasks: mockResponse.tasks,
        logs: mockResponse.logs,
        errors: mockResponse.errors,
      }

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => invalidResponse,
      })

      await expect(client.runAgent(mockRequest)).rejects.toThrow(BackendAPIError)
      
      try {
        await client.runAgent(mockRequest)
      } catch (error) {
        expect(error).toBeInstanceOf(BackendAPIError)
        expect((error as BackendAPIError).errorDetail.code).toBe('INVALID_RESPONSE')
        expect((error as BackendAPIError).errorDetail.message).toContain('stats')
      }
    })

    it('should validate response structure - missing logs', async () => {
      const invalidResponse = {
        tasks: mockResponse.tasks,
        stats: mockResponse.stats,
        errors: mockResponse.errors,
      }

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => invalidResponse,
      })

      await expect(client.runAgent(mockRequest)).rejects.toThrow(BackendAPIError)
      
      try {
        await client.runAgent(mockRequest)
      } catch (error) {
        expect(error).toBeInstanceOf(BackendAPIError)
        expect((error as BackendAPIError).errorDetail.code).toBe('INVALID_RESPONSE')
        expect((error as BackendAPIError).errorDetail.message).toContain('logs')
      }
    })

    it('should validate response structure - missing errors', async () => {
      const invalidResponse = {
        tasks: mockResponse.tasks,
        stats: mockResponse.stats,
        logs: mockResponse.logs,
      }

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => invalidResponse,
      })

      await expect(client.runAgent(mockRequest)).rejects.toThrow(BackendAPIError)
      
      try {
        await client.runAgent(mockRequest)
      } catch (error) {
        expect(error).toBeInstanceOf(BackendAPIError)
        expect((error as BackendAPIError).errorDetail.code).toBe('INVALID_RESPONSE')
        expect((error as BackendAPIError).errorDetail.message).toContain('errors')
      }
    })

    it('should validate response structure - not an object', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => 'invalid',
      })

      await expect(client.runAgent(mockRequest)).rejects.toThrow(BackendAPIError)
      
      try {
        await client.runAgent(mockRequest)
      } catch (error) {
        expect(error).toBeInstanceOf(BackendAPIError)
        expect((error as BackendAPIError).errorDetail.code).toBe('INVALID_RESPONSE')
        expect((error as BackendAPIError).errorDetail.message).toContain('not a valid object')
      }
    })
  })
})
