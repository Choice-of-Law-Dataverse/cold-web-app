import { useApiClient } from '@/composables/useApiClient'
import { useQuery } from '@tanstack/vue-query'
import { computed, type Ref } from 'vue'
import type { FullTableRequest } from '~/types/api'

const fetchDomesticInstrumentsData = async (filterCompatible: boolean) => {
  const { apiClient } = useApiClient()
  const body: FullTableRequest = {
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

  const instrumentsData = await apiClient('/search/full_table', {
    body,
  })

  // Convert Date to number, sort descending and take the 7 most recent
  instrumentsData.sort((a: any, b: any) => Number(b.Date) - Number(a.Date))
  return instrumentsData
}

export function useDomesticInstruments({
  filterCompatible,
}: {
  filterCompatible: Ref<boolean>
}) {
  return useQuery({
    queryKey: computed(() =>
      filterCompatible.value
        ? ['domesticInstruments', 'compatible']
        : ['domesticInstruments']
    ),
    queryFn: () => fetchDomesticInstrumentsData(filterCompatible.value),
  })
}
