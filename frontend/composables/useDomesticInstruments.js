import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'

const fetchDomesticInstrumentsData = async (filterCompatible) => {
  const config = useRuntimeConfig()
  const payload = {
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

  const response = await fetch(
    `${config.public.apiBaseUrl}/search/full_table`,
    {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    }
  )

  if (!response.ok) {
    throw new Error('Failed to load domestic instruments data')
  }

  const instrumentsData = await response.json()

  // Convert Date to number, sort descending and take the 7 most recent
  instrumentsData.sort((a, b) => Number(b.Date) - Number(a.Date))
  return instrumentsData
}

export function useDomesticInstruments({ filterCompatible }) {
  return useQuery({
    queryKey: filterCompatible
      ? ['domesticInstruments', 'compatible']
      : ['domesticInstruments'],
    queryFn: fetchDomesticInstrumentsData,
  })
}
