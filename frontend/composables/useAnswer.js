import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '~/composables/useApiClient'

const fetchAnswerData = async (answerId) => {
  if (!answerId) {
    throw new Error('Answer ID is required')
  }

  const { apiClient } = useApiClient()

  const body = {
    table: 'Answers',
    id: answerId,
  }

  try {
    const data = await apiClient('/search/details', { body })

    // Check if the API returned an error response
    if (data.error === 'no entry found with the specified id') {
      const error = new Error('no entry found with the specified id')
      error.isNotFound = true
      error.table = 'Question'
      throw error
    }

    return data
  } catch (err) {
    // Handle specific error cases or re-throw
    if (err.message.includes('no entry found')) {
      throw err // Re-throw with original error properties
    }
    throw new Error(`Failed to fetch answer: ${err.message}`)
  }
}

export function useAnswer(answerId) {
  return useQuery({
    queryKey: computed(() => ['answer', answerId]),
    queryFn: () => fetchAnswerData(answerId.value),
    enabled: computed(() => !!answerId.value),
  })
}
