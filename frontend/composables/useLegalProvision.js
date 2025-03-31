import { ref, computed } from 'vue'

export function useLegalProvision({ provisionId, textType, onHasEnglishTranslationUpdate }) {
    const title = ref(null)
    const content = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const hasEnglishTranslation = ref(false)
    const showEnglish = ref(true)
    const provisionData = ref(null)

    const config = useRuntimeConfig()

    const anchorId = computed(() => {
        const articleNumber = title.value
            ? title.value.replace(/\s+/g, '')
            : provisionId.replace(/\s+/g, '')
        return articleNumber
    })

    async function fetchProvisionDetails() {
        const payload = {
            table: 'Domestic Legal Provisions',
            id: provisionId,
        }

        try {
            const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
                method: 'POST',
                headers: {
                    authorization: `Bearer ${config.public.FASTAPI}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            })

            if (!response.ok) {
                throw new Error(`Failed to fetch provision: ${provisionId}`)
            }
            const data = await response.json()

            title.value = data.Article || 'Unknown Article'
            hasEnglishTranslation.value =
                'Full Text of the Provision (English Translation)' in data
            if (onHasEnglishTranslationUpdate) {
                onHasEnglishTranslationUpdate(hasEnglishTranslation.value)
            }

            provisionData.value = data

            content.value = showEnglish.value
                ? data['Full Text of the Provision (English Translation)'] ||
                data['Full Text of the Provision (Original Language)'] ||
                'No content available'
                : data['Full Text of the Provision (Original Language)'] ||
                'No content available'
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'An error occurred'
        } finally {
            loading.value = false
        }
    }

    function updateContent() {
        if (provisionData.value) {
            content.value = showEnglish.value
                ? provisionData.value['Full Text of the Provision (English Translation)'] ||
                'No English translation available'
                : provisionData.value['Full Text of the Provision (Original Language)'] ||
                'No content available'
        }
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