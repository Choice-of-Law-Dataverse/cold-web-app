import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'

const fetchQuestionsData = async () => {
  const config = useRuntimeConfig()
  const jsonPayload = {
    table: 'Questions',
  }

  const response = await fetch(
    `${config.public.apiBaseUrl}/search/full_table`,
    {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jsonPayload),
    }
  )

  if (!response.ok) {
    throw new Error(`Failed to fetch questions: ${response.statusText}`)
  }

  const data = await response.json()

  // Check if the API returned an error response
  if (data.error) {
    throw new Error(data.error)
  }

  return data
}

export function useQuestions(jurisdiction) {
  return useQuery({
    queryKey: ['questions', jurisdiction],
    queryFn: fetchQuestionsData,
    enabled: computed(() => !!jurisdiction.value),
  })
}
