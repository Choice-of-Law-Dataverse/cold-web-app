import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { formatDate } from '@/utils/format.js'
import { useApiClient } from '~/composables/useApiClient'

const fetchCourtDecisionData = async (courtDecisionId) => {
  if (!courtDecisionId) {
    throw new Error('Court decision ID is required')
  }

  const { apiClient } = useApiClient()
  const body = {
    table: 'Court Decisions',
    id: courtDecisionId,
  }

  try {
    const data = await apiClient('/search/details', { body })

    // Check if the API returned an error response
    if (data.error === 'no entry found with the specified id') {
      throw new Error('no entry found with the specified id')
    }

    if (!data) return null

    return {
      ...data,
      'Case Title':
        data['Case Title'] === 'Not found'
          ? data['Case Citation']
          : data['Case Title'],
      'Related Literature': data['Themes'] || '',
      themes: data['Themes'] || '',
      'Case Citation': data['Case Citation'],
      Questions: data['Questions'],
      'Jurisdictions Alpha-3 Code': data['Jurisdictions Alpha-3 Code'],
      'Publication Date ISO': formatDate(data['Publication Date ISO']),
      'Date of Judgment': formatDate(data['Date of Judgment']),
      hasEnglishQuoteTranslation:
        data['Translated Excerpt'] && data['Translated Excerpt'].trim() !== '',
    }
  } catch (err) {
    throw new Error(`Failed to fetch court decision: ${err.message}`)
  }
}

export function useCourtDecision(courtDecisionId) {
  return useQuery({
    queryKey: computed(() => ['courtDecision', courtDecisionId.value]),
    queryFn: () => fetchCourtDecisionData(courtDecisionId.value),
    enabled: computed(() => !!courtDecisionId.value),
  })
}
