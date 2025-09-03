/**
 * Shared API client hook for TanStack Query composables
 * Provides configured fetch function with base URL and headers
 */
export function useApiClient() {
  const config = useRuntimeConfig()

  const apiClient = async (endpoint, options = {}) => {
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
        ...otherOptions,
      }

      if (body) {
        fetchOptions.body = JSON.stringify(body)
      }

      const response = await fetch(
        `${config.public.apiBaseUrl}${endpoint}`,
        fetchOptions
      )

      clearTimeout(timeoutId)

      if (!response.ok) {
        throw new Error(
          `API request failed: ${response.status} ${response.statusText}`
        )
      }

      const data = await response.json()

      if (data?.error) {
        throw new Error(data.error)
      }

      return data
    } catch (err) {
      clearTimeout(timeoutId)
      if (err.name === 'AbortError') {
        throw new Error('Request timed out. Please try again.')
      }
      throw err
    }
  }

  return { apiClient }
}
