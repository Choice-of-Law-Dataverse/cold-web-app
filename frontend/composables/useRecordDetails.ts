import { computed, type Ref } from 'vue'
import { useQuery, useQueries } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import { useErrorHandler } from '@/composables/useErrorHandler'
import type { TableName } from '~/types/api'

const fetchRecordDetails = async (table: TableName, id: string | number) => {
  const { apiClient } = useApiClient()
  return await apiClient('/search/details', { body: { table, id } })
}

type Options =
  | Partial<{
      select: (data: any) => any
      enableErrorHandling: boolean
      redirectOnNotFound: boolean
      showToast: boolean
    }>
  | undefined

export function useRecordDetails(
  table: Ref<TableName>,
  id: Ref<string | number>,
  {
    select,
    enableErrorHandling = true,
    redirectOnNotFound = true,
    showToast = true,
  }: Options = {}
) {
  const { createQueryErrorHandler } = useErrorHandler()

  return useQuery({
    queryKey: computed(() => [table.value, id.value]),
    queryFn: () => fetchRecordDetails(table.value, id.value),
    enabled: computed(() => Boolean(table.value && id.value)),
    select,
    onError: enableErrorHandling
      ? createQueryErrorHandler(table.value, { redirectOnNotFound, showToast })
      : undefined,
  })
}

export function useRecordDetailsList(
  table: Ref<TableName>,
  ids: Ref<Array<string | number>>,
  { select, enableErrorHandling = true }: Options = {}
) {
  const { createQueryErrorHandler } = useErrorHandler()

  const queries = computed(() => {
    const list = ids.value || []
    return list.map((id) => ({
      queryKey: [table.value, id],
      queryFn: () => fetchRecordDetails(table.value, id),
      enabled: Boolean(table.value && id),
      select,
      onError: enableErrorHandling
        ? createQueryErrorHandler(table.value, {
            redirectOnNotFound: false,
            showToast: true,
          })
        : undefined,
    }))
  })

  const results = useQueries({ queries })

  const data = computed(() => results.value.map((r) => r.data))
  const isLoading = computed(() => results.value.some((r) => r.isLoading))
  const hasError = computed(() => results.value.some((r) => r.isError))
  const error = computed(() => results.value.find((r) => r.isError)?.error)

  return { data, isLoading, hasError, error }
}
