import { computed, type Ref } from 'vue'
import { useQuery, useQueries } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import type { TableName } from '~/types/api'

async function fetchRecordDetails<T>(table: TableName, id: string | number) {
  const { apiClient } = useApiClient()
  return await apiClient<T>('/search/details', { body: { table, id } })
}

type Options<T> =
  | Partial<{
      select: (data: T) => T
    }>
  | undefined

export function useRecordDetails<T = Record<string, unknown>>(
  table: Ref<TableName>,
  id: Ref<string | number>,
  { select }: Options<T> = {}
) {
  return useQuery({
    queryKey: computed(() => [table.value, id.value]),
    queryFn: () => fetchRecordDetails<T>(table.value, id.value),
    enabled: computed(() => Boolean(table.value && id.value)),
    select,
  })
}

export function useRecordDetailsList<T = Record<string, unknown>>(
  table: Ref<TableName>,
  ids: Ref<Array<string | number>>,
  { select }: Options<T> = {}
) {
  const queries = computed(() => {
    const list = ids.value || []
    return list.map((id) => ({
      queryKey: [table.value, id],
      queryFn: () => fetchRecordDetails<T>(table.value, id),
      enabled: Boolean(table.value && id),
      ...(select && { select }),
    }))
  })

  const results = useQueries({ queries })

  const data = computed(() => results.value.map((r) => r.data))
  const isLoading = computed(() => results.value.some((r) => r.isLoading))
  const hasError = computed(() => results.value.some((r) => r.isError))
  const error = computed(() => results.value.find((r) => r.isError)?.error)

  return { data, isLoading, hasError, error }
}
