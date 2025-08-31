import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'

const fetchLiteratureTitle = async (ids) => {
  if (!ids) {
    return ''
  }

  const config = useRuntimeConfig()

  // Split IDs if multiple are provided
  const idList = ids.split(',').map((id) => id.trim())

  try {
    const titles = await Promise.all(
      idList.map(async (id) => {
        const jsonPayload = {
          table: 'Literature',
          id: id,
        }
        const response = await fetch(
          `${config.public.apiBaseUrl}/search/details`,
          {
            method: 'POST',
            headers: {
              authorization: `Bearer ${config.public.FASTAPI}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonPayload),
          }
        )
        if (!response.ok) throw new Error('Failed to fetch literature details')
        const data = await response.json()
        return data.Title || 'Unknown Title'
      })
    )
    return titles
  } catch (error) {
    console.error('Error fetching literature title:', error)
    return 'Error'
  }
}

export function useLiteratureTitle(literatureIds) {
  return useQuery({
    queryKey: ['literature', literatureIds],
    queryFn: () => fetchLiteratureTitle(literatureIds.value),
    enabled: computed(() => !!literatureIds.value),
  })
}
