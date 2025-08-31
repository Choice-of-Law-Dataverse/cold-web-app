import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'

const fetchSpecialists = async (jurisdictionName) => {
  if (!jurisdictionName) return []

  const config = useRuntimeConfig()

  try {
    const response = await fetch(
      `${config.public.apiBaseUrl}/search/full_table`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          table: 'Specialists',
          filters: [{ column: 'Jurisdiction', value: jurisdictionName }],
        }),
      }
    )

    if (!response.ok) throw new Error('Failed to fetch specialists')

    return await response.json()
  } catch (error) {
    console.error('Error fetching specialists:', error)
    return []
  }
}

export function useSpecialists(jurisdictionName) {
  return useQuery({
    queryKey: ['specialists', jurisdictionName],
    queryFn: () => fetchSpecialists(jurisdictionName.value),
    enabled: computed(() => !!jurisdictionName.value),
  })
}
