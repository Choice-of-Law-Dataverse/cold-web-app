import { computed, type Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import type { SearchRequest, TableName } from '~/types/api'

const fetchJurisdictionCount = async (
  jurisdiction: string,
  table: TableName
): Promise<number> => {
  if (!jurisdiction) return 0

  const { apiClient } = useApiClient()

  const body: SearchRequest = {
    search_string: '',
    filters: [
      { column: 'jurisdictions', values: [jurisdiction] },
      { column: 'tables', values: [table] },
    ],
    page: 1,
    page_size: 1,
  }

  const data = await apiClient('/search/', { body })
  return data.total_matches || 0
}

export function useCourtDecisionsCount(jurisdictionName: Ref<string>) {
  return useQuery({
    queryKey: ['courtDecisionsCount', jurisdictionName],
    queryFn: () =>
      fetchJurisdictionCount(jurisdictionName.value, 'Court Decisions'),
    enabled: computed(() => !!jurisdictionName.value),
  })
}

export function useDomesticInstrumentsCount(jurisdictionName: Ref<string>) {
  return useQuery({
    queryKey: ['domesticInstrumentsCount', jurisdictionName],
    queryFn: () =>
      fetchJurisdictionCount(jurisdictionName.value, 'Domestic Instruments'),
    enabled: computed(() => !!jurisdictionName.value),
  })
}
