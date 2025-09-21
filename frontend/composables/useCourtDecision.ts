import { computed, type Ref } from 'vue'
import { formatDate } from '@/utils/format.js'
import { useRecordDetails } from '@/composables/useRecordDetails'

type Options = {
  enableErrorHandling?: boolean
  redirectOnNotFound?: boolean
  showToast?: boolean
}

export function useCourtDecision(
  courtDecisionId: Ref<string | number>,
  options: Options = {}
) {
  return useRecordDetails(
    computed(() => 'Court Decisions'),
    courtDecisionId,
    {
      ...options,
      select: (data) => {
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
            data['Translated Excerpt'] &&
            data['Translated Excerpt'].trim() !== '',
        }
      },
    }
  )
}
