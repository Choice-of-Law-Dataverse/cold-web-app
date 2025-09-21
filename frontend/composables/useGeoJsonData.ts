import { useQuery } from '@tanstack/vue-query'
import { useErrorHandler } from '@/composables/useErrorHandler'

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
  const { createQueryErrorHandler } = useErrorHandler()

  return useQuery({
    queryKey: ['geoJsonData'],
    queryFn: fetchGeoJsonData,
    onError: options.enableErrorHandling
      ? createQueryErrorHandler('GeoJSON Data', {
          redirectOnNotFound: options.redirectOnNotFound,
          showToast: options.showToast,
        })
      : undefined,
  })
}
