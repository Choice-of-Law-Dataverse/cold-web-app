import { useQuery } from '@tanstack/vue-query'
const fetchJurisdictionChartData = async () => {
  const response = await fetch('count_jurisdictions.json')
  const data = await response.json()

  // Transform the JSON data for Plotly
  const xValues = data.map((item: Record<string, unknown>) => item.n) // Extract 'n' values
  const yValues = data.map((item: Record<string, unknown>) => item.jurisdiction) // Extract 'Jurisdiction.Names'
  const links = data.map((item: Record<string, unknown>) => item.url) // Extract URLs

  return {
    xValues,
    yValues,
    links,
  }
}

export function useJurisdictionChart() {
  return useQuery({
    queryKey: ['jurisdictionChart'],
    queryFn: fetchJurisdictionChartData,
  })
}
