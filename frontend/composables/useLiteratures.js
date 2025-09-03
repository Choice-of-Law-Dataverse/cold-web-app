import { computed } from 'vue'
import { useQueries } from '@tanstack/vue-query'
import { useApiClient } from '~/composables/useApiClient'

const fetchLiteratureData = async (literatureId) => {
  const { apiClient } = useApiClient()

  const body = {
    table: 'Literature',
    id: literatureId,
  }

  try {
    const data = await apiClient('/search/details', { body })

    // Check if the API returned an error response
    if (data.error === 'no entry found with the specified id') {
      const error = new Error('no entry found with the specified id')
      error.isNotFound = true
      error.table = 'Literature'
      throw error
    }

    return data
  } catch (err) {
    // Handle specific error cases or re-throw
    if (err.message.includes('no entry found')) {
      throw err // Re-throw with original error properties
    }
    throw new Error(`Failed to fetch literature: ${err.message}`)
  }
}

export function useLiteratures(ids) {
  const queries = computed(() => {
    const literatureIds = ids.value
      ? ids.value
          .split(',')
          .map((id) => id.trim())
          .filter((id) => id)
      : []

    console.log('Literature IDs:', literatureIds)

    return literatureIds.map((literatureId) => ({
      queryKey: ['literature', literatureId],
      queryFn: () => fetchLiteratureData(literatureId),
      enabled: !!literatureId,
    }))
  })

  const results = useQueries({
    queries: queries,
  })

  const data = computed(() => {
    console.log(
      'Literatures data:',
      results.value.map((result) => result.data)
    )
    return results.value.map((result) => result.data)
  })

  const isLoading = computed(() => {
    return results.value.some((result) => result.isLoading)
  })

  const hasError = computed(() => {
    return results.value.some((result) => result.isError)
  })

  return {
    isLoading,
    hasError,
    results,
    data,
  }
}
