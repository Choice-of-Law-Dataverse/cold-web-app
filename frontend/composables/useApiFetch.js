import { ref } from 'vue'

export function useApiFetch() {
  const loading = ref(true)
  const error = ref(null)
  const data = ref(null)

  const fetchData = async ({ table, id }) => {
    loading.value = true
    error.value = null
    data.value = null

    const config = useRuntimeConfig()
    const jsonPayload = { table, id }

    try {
      // Create an AbortController for timeout
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000) // 30 second timeout

      const response = await fetch(`/api/proxy/search/details`, {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonPayload),
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        throw new Error(
          `Failed to fetch ${table}: ${response.status} ${response.statusText}`
        )
      }

      const responseData = await response.json()

      // Check if the API returned a "not found" error
      if (responseData.error === 'no entry found with the specified id') {
        const error = new Error('no entry found with the specified id')
        error.isNotFound = true
        error.table = table
        throw error
      }

      if (!responseData) {
        throw new Error(`No data received for ${table}`)
      }

      data.value = responseData
      return data.value
    } catch (err) {
      if (err.name === 'AbortError') {
        error.value = 'Request timed out. Please try again.'
      } else {
        error.value =
          err instanceof Error
            ? err.message
            : 'An error occurred while fetching data'
      }
      console.error('API Fetch Error:', error.value)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    data,
    fetchData,
  }
}
