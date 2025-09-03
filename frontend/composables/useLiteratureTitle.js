import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '~/composables/useApiClient'

const fetchLiteratureTitle = async (ids) => {
  if (!ids) {
    return ''
  }

  const { apiClient } = useApiClient()

  // Split IDs if multiple are provided
  const idList = ids.split(',').map((id) => id.trim())

  try {
    return await Promise.all(
      idList.map(async (id) => {
        const body = {
          table: 'Literature',
          id: id,
        }
        const data = await apiClient('/search/details', { body })
        return data.Title || 'Unknown Title'
      })
    )
  } catch (err) {
    console.error('Error fetching literature title:', err)
    throw new Error(`Failed to fetch literature titles: ${err.message}`)
  }
}

export function useLiteratureTitle(literatureIds) {
  return useQuery({
    queryKey: ['literature', literatureIds],
    queryFn: () => fetchLiteratureTitle(literatureIds.value),
    enabled: computed(() => !!literatureIds.value),
  })
}
