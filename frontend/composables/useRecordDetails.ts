import { computed, type Ref } from 'vue'
import { useQuery, useQueries } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import type { TableName } from '~/types/api'

const fetchRecordDetails = async (table: TableName, id: string | number) => {
  const { apiClient } = useApiClient()
  return await apiClient('/search/details', { body: { table, id } })
}

export function useRecordDetails(
  table: Ref<TableName>,
  id: Ref<string | number>
) {
  return useQuery({
    queryKey: computed(() => [table.value, id.value]),
    queryFn: () => fetchRecordDetails(table.value, id.value),
    enabled: computed(() => Boolean(table.value && id.value)),
  })
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
    }))
  })

  const results = useQueries({ queries })

  const data = computed(() => results.value.map((r) => r.data))
  const isLoading = computed(() => results.value.some((r) => r.isLoading))
  const hasError = computed(() => results.value.some((r) => r.isError))
  const error = computed(() => results.value.find((r) => r.isError)?.error)

  return { data, isLoading, hasError, error }
}
