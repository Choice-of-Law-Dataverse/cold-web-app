import { ref, computed, watch } from 'vue'
import { questionConfig } from '~/config/pageConfigs'

export function useQuestions() {
  const questionsData = ref([])
  const loading = ref(true)
  const error = ref(null)
  const answersLoading = ref(false)

  const config = useRuntimeConfig()

  const keyLabelPairs = questionConfig.keyLabelPairs
  const valueClassMap = questionConfig.valueClassMap

  // Store all answers keyed by answer ID
  const answersMap = ref({})

  // Fetch answer for a specific ID
  async function fetchAnswer(answerId) {
    try {
      const response = await fetch(
        `${config.public.apiBaseUrl}/search/details`,
        {
          method: 'POST',
          headers: {
            authorization: `Bearer ${config.public.FASTAPI}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ table: 'Answers', id: answerId }),
        }
      )
      if (!response.ok) {
        throw new Error(`Failed to fetch answer: ${response.statusText}`)
      }
      const data = await response.json()
      return data.Answer || ''
    } catch (err) {
      console.error(`Error fetching answer for ${answerId}:`, err)
      return ''
    }
  }

  // Fetch answers for all questions
  async function fetchAllAnswers() {
    if (!questionsData.value || !Array.isArray(questionsData.value)) return

    answersLoading.value = true

    // Get ISO3 code from the URL
    let iso3 = ''
    if (typeof window !== 'undefined') {
      const match = window.location.pathname.match(/\/jurisdiction\/([^/]+)/)
      if (match && match[1]) {
        iso3 = match[1].toUpperCase()
      }
    }

    try {
      // Create promises for all answer fetches
      const answerPromises = questionsData.value.map(async (item) => {
        const answerId = iso3 ? `${iso3}_${item.ID}` : item.ID
        const answer = await fetchAnswer(answerId)
        return { id: answerId, answer }
      })

      // Wait for all answers to be fetched
      const results = await Promise.all(answerPromises)

      // Build the answers map
      const newAnswersMap = {}
      results.forEach(({ id, answer }) => {
        newAnswersMap[id] = answer
      })

      answersMap.value = newAnswersMap
    } catch (err) {
      console.error('Error fetching answers:', err)
    } finally {
      answersLoading.value = false
    }
  }

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
      // Get ISO3 code from the URL (assume /jurisdiction/[id]) and uppercase it
      let iso3 = ''
      if (typeof window !== 'undefined') {
        const match = window.location.pathname.match(/\/jurisdiction\/([^/]+)/)
        if (match && match[1]) {
          iso3 = match[1].toUpperCase()
        }
      }

      const answerId = iso3 ? `${iso3}_${item['ID']}` : item['ID']
      const answerText = answersMap.value[answerId] || ''

      // Replace commas with '; ' if multiple answers are present
      let answerDisplay = answerText
      if (typeof answerText === 'string' && answerText.includes(',')) {
        answerDisplay = answerText
          .split(',')
          .map((s) => s.trim())
          .join('; ')
      }
      return {
        id,
        question: item.Question,
        theme: item['Themes Link'],
        answer: answerDisplay,
        answerLink: `/question/${answerId}`,
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

      // After questions are loaded, fetch the answers
      await fetchAllAnswers()
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
    answersLoading,
    answersMap,
    processedQuestionsData,
    filteredKeyLabelPairs,
    valueClassMap,
    fetchQuestions,
    fetchAllAnswers,
  }
}
