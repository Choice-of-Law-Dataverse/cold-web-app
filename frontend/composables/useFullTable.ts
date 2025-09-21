import { useQuery, type UseQueriesOptions } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import { useErrorHandler } from '@/composables/useErrorHandler'
import type { FullTableRequest, TableName } from '~/types/api'

const fetchFullTableData = async (
  table: TableName,
  filters: FullTableRequest['filters'] = []
): Promise<any[]> => {
  const { apiClient } = useApiClient()
  const body: FullTableRequest = { table, filters }

  return await apiClient('/search/full_table', { body })
}

type Options =
  | Partial<{
      select: (data: any[]) => any[]
      filters: FullTableRequest['filters']
      enableErrorHandling: boolean
      redirectOnNotFound: boolean
      showToast: boolean
    }>
  | undefined

export function useFullTable(
  table: TableName,
  {
    select,
    filters,
    enableErrorHandling = true,
    redirectOnNotFound = false, // For full table queries, usually prefer toast over redirect
    showToast = true,
  }: Options = {}
) {
  const { createQueryErrorHandler } = useErrorHandler()

  return useQuery({
    queryKey: [
      table,
      filters ? filters.map((f) => f.value).join(',') : undefined,
    ],
    queryFn: () => fetchFullTableData(table, filters),
    select,
    onError: enableErrorHandling
      ? createQueryErrorHandler(table, { redirectOnNotFound, showToast })
      : undefined,
  })
}
