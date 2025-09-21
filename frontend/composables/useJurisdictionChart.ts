import { useQuery } from '@tanstack/vue-query'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { watch } from 'vue'

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
  const { handleError } = useErrorHandler()

  const queryResult = useQuery({
    queryKey: ['jurisdictionChart'],
    queryFn: fetchJurisdictionChartData,
    throwOnError: false, // Don't throw errors, handle them manually
  })

  // Watch for errors and handle them reactively when error handling is enabled
  watch(
    () => queryResult.error.value,
    (error) => {
      if (options.enableErrorHandling && error) {
        handleError(error, undefined, {
          redirectOnNotFound: options.redirectOnNotFound,
          showToast: options.showToast,
        })
      }
    },
    { immediate: true }
  )

  return queryResult
}
