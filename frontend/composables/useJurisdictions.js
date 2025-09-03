import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '~/composables/useApiClient'

const fetchJurisdictionsData = async () => {
  const { apiClient } = useApiClient()
  const body = { table: 'Jurisdictions', filters: [] }

  try {
    const data = await apiClient('/search/full_table', { body })

    // Filter jurisdictions (only relevant ones)
    const relevantJurisdictions = data.filter(
      (entry) => entry['Irrelevant?'] === false
    )

    // Extract "Name" field
    const jurisdictionNames = relevantJurisdictions
      .map((entry) => entry.Name)
      .filter(Boolean)

    // Sort alphabetically
    return [...new Set(jurisdictionNames)].sort((a, b) => a.localeCompare(b))
  } catch (err) {
    throw new Error(`Failed to load jurisdictions data: ${err.message}`)
  }
}

export function useJurisdictions() {
  return useQuery({
    queryKey: ['jurisdictions'],
    queryFn: fetchJurisdictionsData,
  })
}
