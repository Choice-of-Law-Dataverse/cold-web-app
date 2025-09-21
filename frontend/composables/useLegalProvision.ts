import { ref, computed, watch } from 'vue'
import { useRecordDetails } from './useRecordDetails'
import type { TableName } from '~/types/api'

export function useLegalProvision({
  provisionId,
  textType,
  onHasEnglishTranslationUpdate,
  table = 'Domestic Legal Provisions', // default table
}: {
  provisionId: string
  textType: string
  onHasEnglishTranslationUpdate?: (hasTranslation: boolean) => void
  table?: TableName
}) {
  const hasEnglishTranslation = ref(false)
  const showEnglish = ref(true)

  // Use TanStack Vue Query for data fetching
  const tableRef = ref(table)
  const idRef = ref(provisionId)

  const {
    data: provisionData,
    isLoading: loading,
    error,
  } = useRecordDetails(tableRef, idRef)

  // Computed properties derived from the fetched data
  const title = computed(() => {
    if (!provisionData.value) return ''
    return table === 'Regional Legal Provisions'
      ? provisionData.value['Title of the Provision'] || 'Unknown Article'
      : provisionData.value.Article || 'Unknown Article'
  })

  const content = computed(() => {
    if (!provisionData.value) return ''

    return showEnglish.value
      ? (table === 'Regional Legal Provisions'
          ? provisionData.value['Full Text']
          : provisionData.value[
              'Full Text of the Provision (English Translation)'
            ]) ||
          provisionData.value[
            'Full Text of the Provision (Original Language)'
          ] ||
          'No content available'
      : provisionData.value['Full Text of the Provision (Original Language)'] ||
          'No content available'
  })

  const anchorId = computed(() => {
    const articleNumber = title.value
      ? title.value.replace(/\s+/g, '')
      : provisionId.replace(/\s+/g, '')
    return articleNumber
  })

  // Watch for data changes to update hasEnglishTranslation
  watch(
    provisionData,
    (newData) => {
      if (newData) {
        hasEnglishTranslation.value =
          'Full Text of the Provision (English Translation)' in newData

        if (onHasEnglishTranslationUpdate) {
          onHasEnglishTranslationUpdate(hasEnglishTranslation.value)
        }
      }
    },
    { immediate: true }
  )

  function updateContent() {
    // This function now triggers a reactivity update by changing showEnglish
    // The computed content will automatically update
  }

  // For backwards compatibility, provide a fetchProvisionDetails function
  function fetchProvisionDetails() {
    // With TanStack Query, this is handled automatically
    // We can update the refs to trigger a refetch if needed
    idRef.value = provisionId
    tableRef.value = table
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
