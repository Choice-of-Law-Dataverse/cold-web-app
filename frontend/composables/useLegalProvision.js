import { ref, computed } from 'vue'
import { useApiFetch } from './useApiFetch'

export function useLegalProvision({
    provisionId,
    textType,
    onHasEnglishTranslationUpdate
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
        console.log('Fetching provision details for ID:', provisionId)
        loading.value = true
        error.value = null

        try {
            console.log('Making API request with:', {
                table: 'Domestic Legal Provisions',
                id: provisionId
            })
            const data = await fetchData({
                table: 'Domestic Legal Provisions',
                id: provisionId,
            })
            console.log('API response:', data)

            if (!data) {
                throw new Error('No data received')
            }

            title.value = data.Article || 'Unknown Article'
            hasEnglishTranslation.value = 'Full Text of the Provision (English Translation)' in data
            provisionData.value = data

            // Set initial content to English first, then fallback to Original Language
            content.value = showEnglish.value
                ? data['Full Text of the Provision (English Translation)'] ||
                data['Full Text of the Provision (Original Language)'] ||
                'No content available'
                : data['Full Text of the Provision (Original Language)'] ||
                'No content available'

            if (onHasEnglishTranslationUpdate) {
                onHasEnglishTranslationUpdate(hasEnglishTranslation.value)
            }
        } catch (err) {
            console.error('Error fetching provision details:', err)
            error.value = err instanceof Error ? err.message : 'Failed to fetch provision details'
        } finally {
            loading.value = false
        }
    }

    function updateContent() {
        if (!provisionData.value) return

        content.value = showEnglish.value
            ? provisionData.value['Full Text of the Provision (English Translation)'] ||
            'No English translation available'
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
        updateContent
    }
} 