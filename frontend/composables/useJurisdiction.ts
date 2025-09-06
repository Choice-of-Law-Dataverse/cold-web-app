import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import type { DetailsByIdRequest } from '~/types/api'

const fetchJurisdictionData = async (jurisdictionIso3: string) => {
  if (!jurisdictionIso3) {
    throw new Error('ISO3 code is required')
  }

  const { apiClient } = useApiClient()
  const body: DetailsByIdRequest = {
    table: 'Jurisdictions',
    id: jurisdictionIso3.toUpperCase(),
  }

  const data = await apiClient('/search/details', { body })

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

export function useJurisdiction(iso3: Ref<string>) {
  return useQuery({
    queryKey: ['jurisdiction', iso3],
    queryFn: () => fetchJurisdictionData(iso3.value),
    enabled: computed(() => !!iso3.value),
  })
}
