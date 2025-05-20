import { ref, computed } from 'vue'
import { useApiFetch } from './useApiFetch'

export function useLegalProvision({
  provisionId,
  textType,
  onHasEnglishTranslationUpdate,
  table = 'Domestic Legal Provisions', // default table
}) {
  const title = ref('')
  const content = ref('')
  const loading = ref(true)
  const error = ref(null)
  const hasEnglishTranslation = ref(false)
  const showEnglish = ref(true)
  const provisionData = ref(null)
  const anchorId = computed(() => {
    const articleNumber = title.value
      ? title.value.replace(/\s+/g, '')
      : provisionId.replace(/\s+/g, '')
    return articleNumber
  })

  const { fetchData } = useApiFetch()

  async function fetchProvisionDetails() {
    loading.value = true
    error.value = null

    try {
      const data = await fetchData({
        table, // use the passed-in table
        id: provisionId,
      })

      if (!data) {
        throw new Error('No data received')
      }

      title.value =
        table === 'Regional Legal Provisions'
          ? data['Title of the Provision'] || 'Unknown Article'
          : data.Article || 'Unknown Article'
      hasEnglishTranslation.value =
        'Full Text of the Provision (English Translation)' in data
      provisionData.value = data

      // Set initial content to English first, then fallback to Original Language
      content.value = showEnglish.value
        ? (table === 'Regional Legal Provisions'
            ? data['Full Text']
            : data['Full Text of the Provision (English Translation)']) ||
          data['Full Text of the Provision (Original Language)'] ||
          'No content available'
        : data['Full Text of the Provision (Original Language)'] ||
          'No content available'

      if (onHasEnglishTranslationUpdate) {
        onHasEnglishTranslationUpdate(hasEnglishTranslation.value)
      }
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch provision details'
    } finally {
      loading.value = false
    }
  }

  function updateContent() {
    if (!provisionData.value) return

    content.value = showEnglish.value
      ? (table === 'Regional Legal Provisions'
          ? provisionData.value['Full Text']
          : provisionData.value[
              'Full Text of the Provision (English Translation)'
            ]) || 'No English translation available'
      : provisionData.value['Full Text of the Provision (Original Language)'] ||
        'No content available'
  }

  return {
    title,
    content,
    loading,
    error,
    hasEnglishTranslation,
    showEnglish,
    anchorId,
    fetchProvisionDetails,
    updateContent,
  }
}
