import { computed, type Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import type { FullTableRequest } from '~/types/api'

const fetchSpecialists = async (jurisdictionName: string): Promise<any[]> => {
  if (!jurisdictionName) return []

  const { apiClient } = useApiClient()

  const body: FullTableRequest = {
    table: 'Specialists',
    filters: [{ column: 'Jurisdiction', value: jurisdictionName }],
  }

  return await apiClient('/search/full_table', { body })
}

export function useSpecialists(jurisdictionName: Ref<string>) {
  return useQuery({
    queryKey: ['specialists', jurisdictionName],
    queryFn: () => fetchSpecialists(jurisdictionName.value),
    enabled: computed(() => !!jurisdictionName.value),
  })
}
