import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import type { FullTableRequest } from '~/types/api'

const fetchJurisdictionsData = async (): Promise<string[]> => {
  const { apiClient } = useApiClient()
  const body: FullTableRequest = { table: 'Jurisdictions', filters: [] }

  const data = await apiClient('/search/full_table', { body })

  // Filter jurisdictions (only relevant ones)
  const relevantJurisdictions = data.filter(
    (entry: any) => entry['Irrelevant?'] === false
  )

  // Extract "Name" field
  const jurisdictionNames: string[] = relevantJurisdictions
    .map((entry: any) => entry.Name)
    .filter(
      (name: any): name is string => Boolean(name) && typeof name === 'string'
    )

  // Sort alphabetically
  const uniqueNames = [...new Set(jurisdictionNames)]
  return uniqueNames.sort((a, b) => a.localeCompare(b))
}

export function useJurisdictions() {
  return useQuery({
    queryKey: ['jurisdictions'],
    queryFn: fetchJurisdictionsData,
  })
}
