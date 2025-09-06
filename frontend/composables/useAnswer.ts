import { computed, type Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import type { DetailsByIdRequest } from '~/types/api'

const fetchAnswerData = async (answerId: string | number) => {
  if (!answerId) {
    throw new Error('Answer ID is required')
  }

  const { apiClient } = useApiClient()

  const body: DetailsByIdRequest = {
    table: 'Answers',
    id: answerId,
  }

  return await apiClient('/search/details', { body })
}

export function useAnswer(answerId: Ref<string | number>) {
  return useQuery({
    queryKey: computed(() => ['answer', answerId.value]),
    queryFn: () => fetchAnswerData(answerId.value),
    enabled: computed(() => !!answerId.value),
  })
}
