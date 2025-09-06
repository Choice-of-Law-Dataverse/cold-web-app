import { computed, type Ref } from 'vue'
import { useQueries } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import type { TableName } from '@/types/api'

const fetchRecordDetails = async (
  table: TableName,
  id: string | number
) => {
  const { apiClient } = useApiClient()
  return await apiClient('/search/details', { body: { table, id } })
}

export function useRecordDetailsList(
  table: Ref<TableName>,
  ids: Ref<Array<string | number>>
) {


  const queries = computed(() => {
    const list = ids.value || []
    return list.map((id) => ({
      queryKey: [table.value, id],
      queryFn: () => fetchRecordDetails(table.value, id),
      enabled: Boolean(table.value && id),
      staleTime: 5 * 60 * 1000,
    }))
  })

  const results = useQueries({ queries })

  const dataMap = computed<Record<string | number, any>>(() => {
    const map: Record<string | number, any> = {}
    results.value.forEach((res, idx) => {
      const id = ids.value?.[idx]
      if (id != null && res.data) map[id] = res.data
    })
    return map
  })

  const isLoading = computed(() => results.value.some((r) => r.isLoading))
  const hasError = computed(() => results.value.some((r) => r.isError))

  return { dataMap, isLoading, hasError, results }
}

