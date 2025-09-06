import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import type { FullTableRequest } from '~/types/api'

const fetchLiteratureByJurisdiction = async (jurisdiction: string) => {
  const { apiClient } = useApiClient()

  const body: FullTableRequest = {
    table: 'Literature',
    filters: [
      {
        column: 'Jurisdiction',
        value: jurisdiction,
      },
    ],
  }

  return await apiClient('/search/full_table', { body })
}

export function useLiteratureByJurisdiction(jurisdiction: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ['literature_jurisdiction', jurisdiction]),
    queryFn: () => fetchLiteratureByJurisdiction(jurisdiction.value),
    enabled: computed(() => !!jurisdiction.value),
  })
}
