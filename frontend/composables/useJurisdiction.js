import { ref, computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { jurisdictionConfig } from '~/config/pageConfigs'

const fetchJurisdictionData = async (jurisdictionIso3) => {
  if (!jurisdictionIso3) {
    throw new Error('ISO3 code is required')
  }

  const config = useRuntimeConfig()
  const jsonPayload = {
    table: 'Jurisdictions',
    id: jurisdictionIso3.toUpperCase(),
  }

  const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
    method: 'POST',
    headers: {
      authorization: `Bearer ${config.public.FASTAPI}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(jsonPayload),
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch jurisdiction: ${response.statusText}`)
  }

  const data = await response.json()

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
}

export function useJurisdiction(iso3) {
  return useQuery({
    queryKey: ['jurisdiction', iso3],
    queryFn: () => fetchJurisdictionData(iso3.value),
    enabled: computed(() => !!iso3.value),
  })
}
