import type { ApiRequestBody, ApiResponse } from '~/types/api'
import { ApiError, NotFoundError } from '~/types/errors'

/**
 * Shared API client hook for TanStack Query composables
 * Provides configured fetch function with base URL and headers
 */
export function useApiClient() {
  const config = useRuntimeConfig()

  const apiClient = async <T = any>(
    endpoint: string,
    options: {
      body?: ApiRequestBody
      method?: string
      timeout?: number
      headers?: Record<string, string>
    } = {}
  ): Promise<T> => {
    const { body, method = 'POST', timeout = 30000, ...otherOptions } = options

    // Create an AbortController for timeout
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    try {
      const fetchOptions = {
        method,
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
          ...otherOptions.headers,
        },
        signal: controller.signal,
        body: body ? JSON.stringify(body) : undefined,
        ...otherOptions,
      }

      const response = await fetch(
        `${config.public.apiBaseUrl}${endpoint}`,
        fetchOptions
      )

      if (!response.ok) {
        if (response.status === 404) {
          throw new NotFoundError(
            endpoint,
            method,
            body,
            new Error(`HTTP ${response.status}: ${response.statusText}`)
          )
        }

        throw new ApiError(
          endpoint,
          method,
          body,
          new Error(`HTTP ${response.status}: ${response.statusText}`)
        )
      }

      const data = await response.json()

      if (data?.error) {
        // Check if the error indicates a not found condition
        const errorMessage = data.error.toLowerCase()
        if (
          errorMessage.includes('not found') ||
          errorMessage.includes('no entry found')
        ) {
          throw new NotFoundError(endpoint, method, body, new Error(data.error))
        }

        throw new ApiError(endpoint, method, body, new Error(data.error))
      }

      return data
    } catch (err) {
      if (err instanceof ApiError || err instanceof NotFoundError) {
        throw err // Re-throw custom errors as-is
      }

      if (err instanceof Error && err.name === 'AbortError') {
        throw new ApiError(
          endpoint,
          method,
          body,
          err,
          'Request timed out. Please try again.'
        )
      }

      throw new ApiError(endpoint, method, body, err)
    } finally {
      clearTimeout(timeoutId)
    }
  }

  return { apiClient }
}
