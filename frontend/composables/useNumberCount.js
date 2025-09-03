import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '~/composables/useApiClient'

const fetchNumberCount = async (tableName) => {
  if (!tableName) {
    return 0
  }

  const { apiClient } = useApiClient()

  const body = {
    search_string: '',
    filters: [
      {
        column: 'tables',
        values: [tableName],
      },
    ],
  }

  try {
    const data = await apiClient('/search/', { body })
    return data.total_matches ?? 0
  } catch (err) {
    throw new Error(`Failed to fetch number count: ${err.message}`)
  }
}

export function useNumberCount(tableName) {
  return useQuery({
    queryKey: ['numberCount', tableName],
    queryFn: () => fetchNumberCount(tableName.value),
    enabled: computed(() => !!tableName.value),
  })
}
