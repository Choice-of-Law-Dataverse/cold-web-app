import { computed, type Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { formatDate } from '@/utils/format.js'
import { useApiClient } from '@/composables/useApiClient'
import type { DetailsByIdRequest } from '~/types/api'

const fetchCourtDecisionData = async (courtDecisionId: string | number) => {
  if (!courtDecisionId) {
    throw new Error('Court decision ID is required')
  }

  const { apiClient } = useApiClient()

  const body: DetailsByIdRequest = {
    table: 'Court Decisions',
    id: courtDecisionId,
  }

  const data = await apiClient('/search/details', { body })

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
}

export function useCourtDecision(courtDecisionId: Ref<string | number>) {
  return useQuery({
    queryKey: computed(() => ['courtDecision', courtDecisionId.value]),
    queryFn: () => fetchCourtDecisionData(courtDecisionId.value),
    enabled: computed(() => !!courtDecisionId.value),
  })
}
