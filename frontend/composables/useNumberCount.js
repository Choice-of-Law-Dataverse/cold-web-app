import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'

const fetchNumberCount = async (tableName) => {
  if (!tableName) {
    return 0
  }

  const config = useRuntimeConfig()

  const body = {
    search_string: '',
    filters: [
      {
        column: 'tables',
        values: [tableName],
      },
    ],
  }

  const response = await fetch(`${config.public.apiBaseUrl}/search/`, {
    method: 'POST',
    headers: {
      authorization: `Bearer ${config.public.FASTAPI}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch number count: ${response.statusText}`)
  }

  const data = await response.json()
  return data.total_matches ?? 0
}

export function useNumberCount(tableName) {
  return useQuery({
    queryKey: ['numberCount', tableName],
    queryFn: () => fetchNumberCount(tableName.value),
    enabled: computed(() => !!tableName.value),
  })
}
