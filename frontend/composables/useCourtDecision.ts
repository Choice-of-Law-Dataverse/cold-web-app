import { computed, type Ref } from 'vue'
import { formatDate } from '@/utils/format.js'
import { useRecordDetails } from '@/composables/useRecordDetails'

export function useCourtDecision(courtDecisionId: Ref<string | number>) {
  const base = useRecordDetails(
    computed(() => 'Court Decisions'),
    courtDecisionId
  )
  const data = computed(() => {
    const rec = base.data.value
    if (!rec) return null
    return {
      ...rec,
      'Case Title':
        rec['Case Title'] === 'Not found'
          ? rec['Case Citation']
          : rec['Case Title'],
      'Related Literature': rec['Themes'] || '',
      themes: rec['Themes'] || '',
      'Case Citation': rec['Case Citation'],
      Questions: rec['Questions'],
      'Jurisdictions Alpha-3 Code': rec['Jurisdictions Alpha-3 Code'],
      'Publication Date ISO': formatDate(rec['Publication Date ISO']),
      'Date of Judgment': formatDate(rec['Date of Judgment']),
      hasEnglishQuoteTranslation:
        rec['Translated Excerpt'] && rec['Translated Excerpt'].trim() !== '',
    }
  })
  return { ...base, data }
}
