import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '~/composables/useApiClient'

const fetchJurisdictionChartData = async () => {
  const { apiClient } = useApiClient()

  const body = {
    table: 'Jurisdictions',
  }

  try {
    const data = await apiClient('/search/full_table', { body })

    // Transform the JSON data for Plotly
    const xValues = data.map((item) => item.n) // Extract 'n' values
    const yValues = data.map((item) => item.jurisdiction) // Extract 'Jurisdiction.Names'
    const links = data.map((item) => item.url) // Extract URLs

    return {
      xValues,
      yValues,
      links,
      rawData: data,
    }
  } catch (error) {
    console.error('Error fetching jurisdiction chart data:', error)
    throw new Error(`Failed to fetch jurisdiction chart data: ${error.message}`)
  }
}

export function useJurisdictionChart() {
  return useQuery({
    queryKey: ['jurisdictionChart'],
    queryFn: fetchJurisdictionChartData,
  })
}
