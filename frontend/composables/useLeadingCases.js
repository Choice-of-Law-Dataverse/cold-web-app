import { useQuery } from '@tanstack/vue-query'
import { formatYear } from '@/utils/format'
import { useApiClient } from '~/composables/useApiClient'

const fetchLeadingCases = async () => {
  const { apiClient } = useApiClient()

  const body = {
    table: 'Court Decisions',
    filters: [
      {
        column: 'Case Rank',
        value: 10,
      },
    ],
  }

  try {
    const decisionsData = await apiClient('/search/full_table', { body })

    // Sort by publication date descending
    decisionsData.sort(
      (a, b) =>
        formatYear(b['Publication Date ISO']) -
        formatYear(a['Publication Date ISO'])
    )

    return decisionsData
  } catch (err) {
    throw new Error(`Failed to load leading cases data: ${err.message}`)
  }
}

export function useLeadingCases() {
  return useQuery({
    queryKey: ['leadingCases'],
    queryFn: fetchLeadingCases,
  })
}
