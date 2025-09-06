import { useQuery } from '@tanstack/vue-query'
import { formatYear } from '@/utils/format'
import { useApiClient } from '@/composables/useApiClient'
import type { FullTableRequest } from '~/types/api'

const fetchLeadingCases = async () => {
  const { apiClient } = useApiClient()

  const body: FullTableRequest = {
    table: 'Court Decisions',
    filters: [
      {
        column: 'Case Rank',
        value: 10,
      },
    ],
  }

  const decisionsData = await apiClient('/search/full_table', { body })

  // Sort by publication date descending
  decisionsData.sort(
    (a: any, b: any) =>
      Number(formatYear(b['Publication Date ISO'])) -
      Number(formatYear(a['Publication Date ISO']))
  )

  return decisionsData
}

export function useLeadingCases() {
  return useQuery({
    queryKey: ['leadingCases'],
    queryFn: fetchLeadingCases,
  })
}
