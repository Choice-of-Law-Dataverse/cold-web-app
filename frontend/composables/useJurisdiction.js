import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'

const fetchJurisdictionData = async (jurisdictionIso3) => {
  if (!jurisdictionIso3) {
    throw new Error('ISO3 code is required')
  }

  const { apiClient } = useApiClient()
  const jsonPayload = {
    table: 'Jurisdictions',
    id: jurisdictionIso3.toUpperCase(),
  }

  try {
    const data = await apiClient('/search/details', { body: jsonPayload })

    // Check if the API returned an error response
    if (data.error === 'no entry found with the specified id') {
      throw new Error('no entry found with the specified id')
    }

    if (!data) return null

    return {
      Name: data?.Name || 'N/A',
      'Jurisdiction Summary': data?.['Jurisdiction Summary'] || 'N/A',
      'Jurisdictional Differentiator':
        data?.['Jurisdictional Differentiator'] || 'N/A',
      'Legal Family': data?.['Legal Family'] || 'N/A',
      Specialists: data?.Specialists || '',
      Literature: data?.Literature,
    }
  } catch (err) {
    throw new Error(`Failed to fetch jurisdiction: ${err.message}`)
  }
}

export function useJurisdiction(iso3) {
  return useQuery({
    queryKey: ['jurisdiction', iso3],
    queryFn: () => fetchJurisdictionData(iso3.value),
    enabled: computed(() => !!iso3.value),
  })
}
