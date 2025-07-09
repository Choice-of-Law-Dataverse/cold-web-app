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
    const sorted = questionsData.value
      .slice()
      .sort((a, b) => a.ID.localeCompare(b.ID))

    // Build a lookup for each level
    const idsByLevel = {}
    for (const item of sorted) {
      const id = item.ID
      const level = typeof id === 'string' ? id.match(/\./g)?.length || 0 : 0
      if (!idsByLevel[level]) idsByLevel[level] = []
      idsByLevel[level].push(id)
    }

    return sorted.map((item, idx, arr) => {
      const id = item.ID
      const level = typeof id === 'string' ? id.match(/\./g)?.length || 0 : 0
      let parentId = null
      if (level > 0) {
        // Find previous id in sorted list with one less period
        for (let j = idx - 1; j >= 0; j--) {
          const prevId = arr[j].ID
          const prevLevel = prevId.match(/\./g)?.length || 0
          if (prevLevel === level - 1) {
            parentId = prevId
            break
          }
        }
      }
      return {
        id,
        question: item.Question,
        theme: item['Themes Link'],
        answer: 'yesh',
        level,
        hasExpand: false,
        expanded: false,
        parentId,
      }
    })
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
