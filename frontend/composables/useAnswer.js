import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'

const fetchAnswerData = async (answerId) => {
  if (!answerId) {
    throw new Error('Answer ID is required')
  }

  const config = useRuntimeConfig()
  const jsonPayload = {
    table: 'Answers',
    id: answerId,
  }

  const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
    method: 'POST',
    headers: {
      authorization: `Bearer ${config.public.FASTAPI}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(jsonPayload),
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch answer: ${response.statusText}`)
  }

  const data = await response.json()

  // Check if the API returned an error response
  if (data.error === 'no entry found with the specified id') {
    const error = new Error('no entry found with the specified id')
    error.isNotFound = true
    error.table = 'Question'
    throw error
  }

  return data
}

export function useAnswer(answerId) {
  return useQuery({
    queryKey: ['answer', answerId],
    queryFn: () => fetchAnswerData(answerId.value),
    enabled: computed(() => !!answerId.value),
  })
}
