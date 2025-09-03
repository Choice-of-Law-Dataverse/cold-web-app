import { useApiClient } from '~/composables/useApiClient'
import { useQuery } from '@tanstack/vue-query'

const fetchDomesticInstrumentsData = async (filterCompatible) => {
  const { apiClient } = useApiClient()
  const body = {
    table: 'Domestic Instruments',
    filters: filterCompatible
      ? [
          {
            column: 'Compatible With the HCCH Principles?',
            value: true,
          },
        ]
      : [],
  }

  try {
    const instrumentsData = await apiClient('/search/full_table', {
      body,
    })

    // Convert Date to number, sort descending and take the 7 most recent
    instrumentsData.sort((a, b) => Number(b.Date) - Number(a.Date))
    return instrumentsData
  } catch (err) {
    throw new Error(`Failed to load domestic instruments data: ${err.message}`)
  }
}

export function useDomesticInstruments({ filterCompatible }) {
  return useQuery({
    queryKey: filterCompatible
      ? ['domesticInstruments', 'compatible']
      : ['domesticInstruments'],
    queryFn: fetchDomesticInstrumentsData,
  })
}
