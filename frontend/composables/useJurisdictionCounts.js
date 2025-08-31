import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'

const fetchJurisdictionCount = async (jurisdiction, table) => {
  if (!jurisdiction) return null

  const config = useRuntimeConfig()
  const payload = {
    search_string: '',
    filters: [
      { column: 'jurisdictions', values: [jurisdiction] },
      { column: 'tables', values: [table] },
    ],
    page: 1,
    page_size: 1,
  }

  const response = await fetch(`${config.public.apiBaseUrl}/search/`, {
    method: 'POST',
    headers: {
      authorization: `Bearer ${config.public.FASTAPI}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error('Failed to fetch count')
  }

  const data = await response.json()
  return data.total_matches || 0
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
