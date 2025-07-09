import { ref, computed, watch } from 'vue'
import { questionConfig } from '~/config/pageConfigs'

export function useQuestions() {
  const questionsData = ref([])
  const loading = ref(true)
  const error = ref(null)

  const config = useRuntimeConfig()

  const keyLabelPairs = questionConfig.keyLabelPairs
  const valueClassMap = questionConfig.valueClassMap

  // Store the answer for the fixed id
  const answer = ref('')

  // Fetch answer for a fixed id (for now)
  async function fetchAnswerForFixedId() {
    try {
      const response = await fetch(
        `${config.public.apiBaseUrl}/search/details`,
        {
          method: 'POST',
          headers: {
            authorization: `Bearer ${config.public.FASTAPI}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ table: 'Answers', id: 'CHE_01.2-P' }),
        }
      )
      if (!response.ok) {
        throw new Error(`Failed to fetch answer: ${response.statusText}`)
      }
      const data = await response.json()
      answer.value = data.Answer || ''
    } catch (err) {
      console.error('Error fetching answer:', err)
      answer.value = ''
    }
  }

  // Fetch answer for the fixed id on load
  fetchAnswerForFixedId()

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

    // Build a map from id to array index for quick lookup
    const idToIndex = {}
    sorted.forEach((item, idx) => {
      idToIndex[item.ID] = idx
    })

    // Precompute children for each id
    const childrenMap = {}
    sorted.forEach((item, idx, arr) => {
      const id = item.ID
      const level = typeof id === 'string' ? id.match(/\./g)?.length || 0 : 0
      let parentId = null
      if (level > 0) {
        for (let j = idx - 1; j >= 0; j--) {
          const prevId = arr[j].ID
          const prevLevel = prevId.match(/\./g)?.length || 0
          if (prevLevel === level - 1) {
            parentId = prevId
            break
          }
        }
      }
      if (parentId) {
        if (!childrenMap[parentId]) childrenMap[parentId] = []
        childrenMap[parentId].push(id)
      }
    })

    return sorted.map((item, idx, arr) => {
      const id = item.ID
      const level = typeof id === 'string' ? id.match(/\./g)?.length || 0 : 0
      let parentId = null
      if (level > 0) {
        for (let j = idx - 1; j >= 0; j--) {
          const prevId = arr[j].ID
          const prevLevel = prevId.match(/\./g)?.length || 0
          if (prevLevel === level - 1) {
            parentId = prevId
            break
          }
        }
      }
      const hasExpand = !!childrenMap[id]
      return {
        id,
        question: item.Question,
        theme: item['Themes Link'],
        answer: answer.value,
        level,
        hasExpand,
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
