import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '~/composables/useApiClient'

const fetchQuestionsData = async () => {
  const { apiClient } = useApiClient()

  const body = {
    table: 'Questions',
  }

  try {
    return await apiClient('/search/full_table', { body })
  } catch (err) {
    throw new Error(`Failed to fetch questions: ${err.message}`)
  }
}

export function useQuestions(jurisdiction) {
  return useQuery({
    queryKey: ['questions', jurisdiction],
    queryFn: fetchQuestionsData,
    enabled: computed(() => !!jurisdiction.value),
  })
}
