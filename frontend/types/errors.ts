import type { ApiRequestBody } from './api'

/**
 * Create a NotFound error using Nuxt's createError
 */
export function createNotFoundError(
  endpoint: string,
  method: string,
  body: ApiRequestBody | undefined,
  originalError: unknown,
  customMessage?: string
) {
  const table = body && 'table' in body ? body.table : undefined
  const id = body && 'id' in body ? body.id : undefined
  const resource = table ? table : endpoint
  const finalMessage = customMessage || `${resource} not found`

  return createError({
    statusCode: 404,
    statusMessage: finalMessage,
    data: {
      name: 'NotFoundError',
      table,
      id,
      endpoint,
      method,
      originalError:
        originalError instanceof Error
          ? {
              name: originalError.name,
              message: originalError.message,
              stack: originalError.stack,
            }
          : originalError,
    }
  })
}

/**
 * Create an API error using Nuxt's createError
 */
export function createApiError(
  endpoint: string,
  method: string,
  body: ApiRequestBody | undefined,
  originalError: unknown,
  customMessage?: string
) {
  const table = body && 'table' in body ? body.table : undefined
  const operation = table ? `fetch ${table}` : `call ${endpoint}`
  const baseErrorMessage =
    originalError instanceof Error ? originalError.message : 'Unknown error'

  const finalMessage =
    customMessage || `Failed to ${operation}: ${baseErrorMessage}`

  return createError({
    statusCode: 500,
    statusMessage: finalMessage,
    data: {
      name: 'ApiError',
      table,
      endpoint,
      method,
      originalError:
        originalError instanceof Error
          ? {
              name: originalError.name,
              message: originalError.message,
              stack: originalError.stack,
            }
          : originalError,
    }
  })
}

/**
 * Custom error class for "not found" errors
 * Used when API returns a 404 or indicates resource not found
 */
export class NotFoundError extends Error {
  public readonly table?: string
  public readonly id?: string | number
  public readonly endpoint: string
  public readonly method: string
  public readonly originalError: unknown
  public readonly body?: ApiRequestBody

  constructor(
    endpoint: string,
    method: string,
    body: ApiRequestBody | undefined,
    originalError: unknown,
    customMessage?: string
  ) {
    // Extract table name from body if available
    const table = body && 'table' in body ? body.table : undefined
    const id = body && 'id' in body ? body.id : undefined

    // Create meaningful error message for not found
    const resource = table ? table : endpoint
    const finalMessage = customMessage || `${resource} not found`

    super(finalMessage)

    this.name = 'NotFoundError'
    this.table = table
    this.id = id
    this.endpoint = endpoint
    this.method = method
    this.body = body
    this.originalError = originalError

    // Maintain proper prototype chain
    Object.setPrototypeOf(this, NotFoundError.prototype)

    console.error(this.toJSON())
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      table: this.table,
      id: this.id,
      endpoint: this.endpoint,
      method: this.method,
      stack: this.stack,
      originalError:
        this.originalError instanceof Error
          ? {
              name: this.originalError.name,
              message: this.originalError.message,
              stack: this.originalError.stack,
            }
          : this.originalError,
    }
  }
}

/**
 * Custom error class for API-related errors
 * Provides structured error information with context about the API call
 */
export class ApiError extends Error {
  public readonly table?: string
  public readonly endpoint: string
  public readonly method: string
  public readonly originalError: unknown
  public readonly body?: ApiRequestBody

  constructor(
    endpoint: string,
    method: string,
    body: ApiRequestBody | undefined,
    originalError: unknown,
    customMessage?: string
  ) {
    // Extract table name from body if available
    const table = body && 'table' in body ? body.table : undefined

    // Create meaningful error message
    const operation = table ? `fetch ${table}` : `call ${endpoint}`
    const baseErrorMessage =
      originalError instanceof Error ? originalError.message : 'Unknown error'

    const finalMessage =
      customMessage || `Failed to ${operation}: ${baseErrorMessage}`

    super(finalMessage)

    this.name = 'ApiError'
    this.table = table
    this.endpoint = endpoint
    this.method = method
    this.body = body
    this.originalError = originalError

    // Maintain proper prototype chain
    Object.setPrototypeOf(this, ApiError.prototype)

    console.error(this.toJSON())
  }

  /**
   * Convert to JSON for logging/debugging
   */
  toJSON() {
    return {
      name: this.name,
      message: this.message,
      table: this.table,
      endpoint: this.endpoint,
      method: this.method,
      stack: this.stack,
      originalError:
        this.originalError instanceof Error
          ? {
              name: this.originalError.name,
              message: this.originalError.message,
              stack: this.originalError.stack,
            }
          : this.originalError,
    }
  }
}
