import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '~/composables/useApiClient'

const fetchJurisdictionCount = async (jurisdiction, table) => {
  if (!jurisdiction) return null

  const { apiClient } = useApiClient()

  const body = {
    search_string: '',
    filters: [
      { column: 'jurisdictions', values: [jurisdiction] },
      { column: 'tables', values: [table] },
    ],
    page: 1,
    page_size: 1,
  }

  try {
    const data = await apiClient('/search/', { body })
    return data.total_matches || 0
  } catch (err) {
    throw new Error(`Failed to fetch count: ${err.message}`)
  }
}

export function useCourtDecisionsCount(jurisdictionName) {
  return useQuery({
    queryKey: ['courtDecisionsCount', jurisdictionName],
    queryFn: () =>
      fetchJurisdictionCount(jurisdictionName.value, 'Court Decisions'),
    enabled: computed(() => !!jurisdictionName.value),
  })
}

export function useDomesticInstrumentsCount(jurisdictionName) {
  return useQuery({
    queryKey: ['domesticInstrumentsCount', jurisdictionName],
    queryFn: () =>
      fetchJurisdictionCount(jurisdictionName.value, 'Domestic Instruments'),
    enabled: computed(() => !!jurisdictionName.value),
  })
}
