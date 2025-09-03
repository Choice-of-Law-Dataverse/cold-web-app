import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '~/composables/useApiClient'

const fetchSpecialists = async (jurisdictionName) => {
  if (!jurisdictionName) return []

  const { apiClient } = useApiClient()

  const body = {
    table: 'Specialists',
    filters: [{ column: 'Jurisdiction', value: jurisdictionName }],
  }

  try {
    return await apiClient('/search/full_table', { body })
  } catch (err) {
    console.error('Error fetching specialists:', err)
    throw new Error(`Failed to fetch specialists: ${err.message}`)
  }
}

export function useSpecialists(jurisdictionName) {
  return useQuery({
    queryKey: ['specialists', jurisdictionName],
    queryFn: () => fetchSpecialists(jurisdictionName.value),
    enabled: computed(() => !!jurisdictionName.value),
  })
}
