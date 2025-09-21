import { useQuery } from '@tanstack/vue-query'
import { useErrorHandler } from '@/composables/useErrorHandler'

const fetchJurisdictionChartData = async () => {
  const response = await fetch('count_jurisdictions.json')
  const data = await response.json()

  // Transform the JSON data for Plotly
  const xValues = data.map((item: any) => item.n) // Extract 'n' values
  const yValues = data.map((item: any) => item.jurisdiction) // Extract 'Jurisdiction.Names'
  const links = data.map((item: any) => item.url) // Extract URLs

  return {
    xValues,
    yValues,
    links,
  }
}

type Options = {
  enableErrorHandling?: boolean
  redirectOnNotFound?: boolean
  showToast?: boolean
}

export function useJurisdictionChart(
  options: Options = {
    enableErrorHandling: true,
    redirectOnNotFound: false, // Chart errors shouldn't redirect
    showToast: true,
  }
) {
  const { createQueryErrorHandler } = useErrorHandler()

  return useQuery({
    queryKey: ['jurisdictionChart'],
    queryFn: fetchJurisdictionChartData,
    onError: options.enableErrorHandling
      ? createQueryErrorHandler('Jurisdiction Chart', {
          redirectOnNotFound: options.redirectOnNotFound,
          showToast: options.showToast,
        })
      : undefined,
  })
}
