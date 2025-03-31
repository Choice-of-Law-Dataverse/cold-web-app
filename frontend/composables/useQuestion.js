import { ref, computed, watch } from 'vue'
import { questionConfig } from '~/config/pageConfigs'

export function useQuestion() {
    const answerData = ref(null)
    const loading = ref(true)
    const error = ref(null)

    const config = useRuntimeConfig()

    const keyLabelPairs = questionConfig.keyLabelPairs
    const valueClassMap = questionConfig.valueClassMap

    // Preprocess data to handle custom rendering cases
    const processedAnswerData = computed(() => {
        if (!answerData.value) return null
        return {
            ...answerData.value,
            'Domestic Legal Provisions':
                answerData.value['Domestic Legal Provisions'] || '',
            'Court Decisions ID': answerData.value['Court Decisions ID']
                ? answerData.value['Court Decisions ID']
                    .split(',')
                    .map((caseId) => caseId.trim())
                : [],
        }
    })

    const filteredKeyLabelPairs = computed(() => {
        if (!processedAnswerData.value) return keyLabelPairs

        const caseIds = processedAnswerData.value['Court Decisions ID']
        const hasRelatedCases = Array.isArray(caseIds) && caseIds.length > 0

        return keyLabelPairs.filter((pair) => {
            if (pair.key === 'Court Decisions ID') {
                return hasRelatedCases
            }
            return true
        })
    })

    async function fetchAnswer(id) {
        loading.value = true
        error.value = null

        const jsonPayload = {
            table: 'Answers',
            id: id,
        }

        try {
            const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
                method: 'POST',
                headers: {
                    authorization: `Bearer ${config.public.FASTAPI}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(jsonPayload),
            })

            if (!response.ok) {
                throw new Error(`Failed to fetch answer: ${response.statusText}`)
            }

            answerData.value = await response.json()
        } catch (err) {
            error.value = err.message
            console.error('Error fetching answer:', err)
        } finally {
            loading.value = false
        }
    }

    return {
        answerData,
        loading,
        error,
        processedAnswerData,
        filteredKeyLabelPairs,
        valueClassMap,
        fetchAnswer,
    }
} 