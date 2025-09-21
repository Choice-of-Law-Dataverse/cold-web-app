import { computed, type Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import { useErrorHandler } from '@/composables/useErrorHandler'
import type { SearchRequest, TableName } from '~/types/api'

const fetchNumberCount = async (tableName: TableName) => {
  if (!tableName) {
    return 0
  }

  const { apiClient } = useApiClient()

  const body: SearchRequest = {
    search_string: '',
    filters: [
      {
        column: 'tables',
        values: [tableName],
      },
    ],
  }

  const data = await apiClient('/search/', { body })
  return data.total_matches ?? 0
}

type Options = {
  enableErrorHandling?: boolean
  redirectOnNotFound?: boolean
  showToast?: boolean
}

export function useNumberCount(
  tableName: Ref<TableName>,
  options: Options = {
    enableErrorHandling: true,
    redirectOnNotFound: false, // Count errors shouldn't redirect
    showToast: true,
  }
) {
  const { createQueryErrorHandler } = useErrorHandler()

  return useQuery({
    queryKey: ['numberCount', tableName],
    queryFn: () => fetchNumberCount(tableName.value),
    enabled: computed(() => !!tableName.value),
    onError: options.enableErrorHandling
      ? createQueryErrorHandler('Number Count', {
          redirectOnNotFound: options.redirectOnNotFound,
          showToast: options.showToast,
        })
      : undefined,
  })
}
