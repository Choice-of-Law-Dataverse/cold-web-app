import { computed, type Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import type { FullTableRequest } from '~/types/api'

const fetchQuestionsData = async () => {
  const { apiClient } = useApiClient()

  const body: FullTableRequest = {
    table: 'Questions',
  }

  return await apiClient('/search/full_table', { body })
}

export function useQuestions(jurisdiction: Ref<string>) {
  return useQuery({
    queryKey: ['questions', jurisdiction],
    queryFn: fetchQuestionsData,
    enabled: computed(() => !!jurisdiction.value),
  })
}
