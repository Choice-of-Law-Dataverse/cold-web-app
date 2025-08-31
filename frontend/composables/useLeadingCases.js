import { useQuery } from '@tanstack/vue-query'
import { formatYear } from '@/utils/format'

const fetchLeadingCases = async () => {
  const config = useRuntimeConfig()
  const payload = {
    table: 'Court Decisions',
    filters: [
      {
        column: 'Case Rank',
        value: 10,
      },
    ],
  }

  const response = await fetch(
    `${config.public.apiBaseUrl}/search/full_table`,
    {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    }
  )

  if (!response.ok) {
    throw new Error('Failed to load leading cases data')
  }

  const decisionsData = await response.json()

  // Sort by publication date descending
  decisionsData.sort(
    (a, b) =>
      formatYear(b['Publication Date ISO']) -
      formatYear(a['Publication Date ISO'])
  )

  return decisionsData
}

export function useLeadingCases() {
  return useQuery({
    queryKey: ['leadingCases'],
    queryFn: fetchLeadingCases,
  })
}
