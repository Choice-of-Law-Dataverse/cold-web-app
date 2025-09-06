import { computed, type Ref } from 'vue'
import { useQueries } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import type { DetailsByIdRequest } from '~/types/api'

const fetchLiteratureData = async (literatureId: string | number) => {
  const { apiClient } = useApiClient()

  const body: DetailsByIdRequest = {
    table: 'Literature',
    id: literatureId,
  }

  return await apiClient('/search/details', { body })
}

export function useLiteratures(ids: Ref<string>) {
  const queries = computed(() => {
    const literatureIds = ids.value
      ? ids.value
          .split(',')
          .map((id: string) => id.trim())
          .filter((id: string) => id)
      : []

    console.log('Literature IDs:', literatureIds)

    return literatureIds.map((literatureId: string) => ({
      queryKey: ['literature', literatureId],
      queryFn: () => fetchLiteratureData(literatureId),
      enabled: !!literatureId,
    }))
  })

  const results = useQueries({
    queries: queries,
  })

  const data = computed(() => {
    console.log(
      'Literatures data:',
      results.value.map((result) => result.data)
    )
    return results.value.map((result) => result.data)
  })

  const isLoading = computed(() => {
    return results.value.some((result) => result.isLoading)
  })

  const hasError = computed(() => {
    return results.value.some((result) => result.isError)
  })

  return {
    isLoading,
    hasError,
    results,
    data,
  }
}
