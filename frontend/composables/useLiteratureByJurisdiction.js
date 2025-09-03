import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '~/composables/useApiClient'

const fetchLiteratureByJurisdiction = async (jurisdiction) => {
  const { apiClient } = useApiClient()

  const body = {
    table: 'Literature',
    filters: [
      {
        column: 'Jurisdiction',
        value: jurisdiction,
      },
    ],
  }

  try {
    const data = await apiClient('/search/full_table', { body })

    if (data.error === 'no entry found with the specified id') {
      const error = new Error('no entry found with the specified id')
      error.isNotFound = true
      error.table = 'Literature'
      throw error
    }

    return data
  } catch (err) {
    if (err.message.includes('no entry found')) {
      throw err
    }
    throw new Error(`Failed to fetch answer: ${err.message}`)
  }
}

export function useLiteratureByJurisdiction(jurisdiction) {
  return useQuery({
    queryKey: computed(() => ['literature_jurisdiction', jurisdiction]),
    queryFn: () => fetchLiteratureByJurisdiction(jurisdiction.value),
    enabled: computed(() => !!jurisdiction.value),
  })
}
