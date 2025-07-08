import { ref, computed, watch } from 'vue'
import { questionConfig } from '~/config/pageConfigs'

export function useQuestions() {
  const questionsData = ref([])
  const loading = ref(true)
  const error = ref(null)

  const config = useRuntimeConfig()

  const keyLabelPairs = questionConfig.keyLabelPairs
  const valueClassMap = questionConfig.valueClassMap

  // Preprocess data to handle custom rendering cases and mapping
  const processedQuestionsData = computed(() => {
    if (!questionsData.value || !Array.isArray(questionsData.value)) return []
    return questionsData.value.map((item) => ({
      id: item.ID,
      question: item.Question,
      theme: item['Theme Code'],
      answer: 'yesh',
      level: 0,
      hasExpand: false, // Default to not expandable
      expanded: false, // Default to collapsed
      parentId: null, // Default to no parent
    }))
  })

  const filteredKeyLabelPairs = computed(() => {
    return keyLabelPairs
  })

  async function fetchQuestions() {
    loading.value = true
    error.value = null

    const jsonPayload = {
      table: 'Questions',
    }

    try {
      const response = await fetch(
        `${config.public.apiBaseUrl}/search/full_table`,
        {
          method: 'POST',
          headers: {
            authorization: `Bearer ${config.public.FASTAPI}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(jsonPayload),
        }
      )

      if (!response.ok) {
        throw new Error(`Failed to fetch questions: ${response.statusText}`)
      }

      const data = await response.json()

      // Check if the API returned an error response
      if (data.error) {
        throw new Error(data.error)
      }

      questionsData.value = data
    } catch (err) {
      error.value = err.message
      console.error('Error fetching questions:', err)
      throw err // Re-throw the error so the page can handle it
    } finally {
      loading.value = false
    }
  }

  return {
    questionsData,
    loading,
    error,
    processedQuestionsData,
    filteredKeyLabelPairs,
    valueClassMap,
    fetchQuestions,
  }
}
