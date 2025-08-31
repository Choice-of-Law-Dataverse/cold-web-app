import { useQuery } from '@tanstack/vue-query'

const fetchJurisdictionChartData = async () => {
  const response = await fetch('count_jurisdictions.json')

  if (!response.ok) {
    throw new Error('Failed to load jurisdiction chart data')
  }

  const jurisdictionData = await response.json()

  // Transform the JSON data for Plotly
  const xValues = jurisdictionData.map((item) => item.n) // Extract 'n' values
  const yValues = jurisdictionData.map((item) => item.jurisdiction) // Extract 'Jurisdiction.Names'
  const links = jurisdictionData.map((item) => item.url) // Extract URLs

  return {
    xValues,
    yValues,
    links,
    rawData: jurisdictionData,
  }
}

export function useJurisdictionChart() {
  return useQuery({
    queryKey: ['jurisdictionChart'],
    queryFn: fetchJurisdictionChartData,
  })
}
