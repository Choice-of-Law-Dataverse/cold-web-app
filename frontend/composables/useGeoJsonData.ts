import { useQuery } from '@tanstack/vue-query'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { watch } from 'vue'

const fetchGeoJsonData = async () => {
  const response = await fetch('/temp_custom.geo.json')
  if (!response.ok) {
    throw new Error('Failed to fetch GeoJSON file')
  }
  return await response.json()
}

type Options = {
  enableErrorHandling?: boolean
  redirectOnNotFound?: boolean
  showToast?: boolean
}

export function useGeoJsonData(
  options: Options = {
    enableErrorHandling: true,
    redirectOnNotFound: false, // GeoJSON errors shouldn't redirect
    showToast: true,
  }
) {
  const { handleError } = useErrorHandler()

  const queryResult = useQuery({
    queryKey: ['geoJsonData'],
    queryFn: fetchGeoJsonData,
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
