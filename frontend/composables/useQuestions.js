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

  // Store all answers keyed by composite answer ID (e.g. CHE_01.1-P)
  const answersMap = ref({})

  /**
   * Fetch all answers for the current jurisdiction in ONE request using /search/full_table.
   * Replaces N calls to /search/details (performance improvement).
   */
  async function fetchAllAnswers() {
    // Need questions loaded (for IDs) but we mainly rely on jurisdiction code.
    answersLoading.value = true

    // Derive ISO3 from URL (/jurisdiction/[code])
    let iso3 = ''
    if (typeof window !== 'undefined') {
      const match = window.location.pathname.match(/\/jurisdiction\/([^/]+)/)
      if (match && match[1]) iso3 = match[1].toUpperCase()
    }

    // If no jurisdiction in URL we cannot batch fetch; leave map empty.
    if (!iso3) {
      answersMap.value = {}
      answersLoading.value = false
      return
    }

    try {
      const payload = {
        table: 'Answers',
        filters: [
          {
            column: 'Jurisdictions Alpha-3 code',
            value: iso3,
          },
        ],
      }

      const response = await fetch(
        `${config.public.apiBaseUrl}/search/full_table`,
        {
          method: 'POST',
          headers: {
            authorization: `Bearer ${config.public.FASTAPI}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        }
      )
      if (!response.ok) {
        throw new Error(`Failed to fetch answers: ${response.statusText}`)
      }
      const data = await response.json()

      // Expect an array of answer rows. We construct the composite key
      // based on either existing 'CoLD ID' or by combining jurisdiction + question ID if needed.
      const map = {}
      if (Array.isArray(data)) {
        for (const row of data) {
          const jurisdiction =
            row['Jurisdictions Alpha-3 code'] ||
            row['Jurisdictions Alpha-3 Code'] ||
            iso3
          const rawQuestionId =
            row['Question ID'] || row['QuestionID'] || row['CoLD ID'] || row.ID
          const rawColdId = row['CoLD ID'] || row['Answer ID'] || rawQuestionId
          const answerValue = row.Answer || row['Answer'] || ''

          // If rawColdId already contains a jurisdiction prefix (ABC_), keep it.
          // Otherwise, build a composite with jurisdiction if available.
          // (Answers table spec: composite = {Jurisdictions Alpha-3 code}_ {Question ID})
          let compositeId
          if (rawColdId && /^[A-Z]{3}_/.test(rawColdId)) {
            compositeId = rawColdId
          } else if (jurisdiction && rawColdId) {
            compositeId = `${jurisdiction}_${rawColdId}`
          } else if (jurisdiction && rawQuestionId) {
            compositeId = `${jurisdiction}_${rawQuestionId}`
          } else {
            compositeId = rawColdId || rawQuestionId
          }

          // Store under composite ID
          if (compositeId) map[compositeId] = answerValue
          // Also store under base ID (without jurisdiction) for any legacy lookups
          if (rawQuestionId && !map[rawQuestionId])
            map[rawQuestionId] = answerValue
        }
      }
      answersMap.value = map
    } catch (err) {
      console.error('Error fetching answers (batch):', err)
    } finally {
      answersLoading.value = false
    }
  }

  // Preprocess data to handle custom rendering cases and mapping
  const processedQuestionsData = computed(() => {
    if (!questionsData.value || !Array.isArray(questionsData.value)) return []
    const sorted = questionsData.value.slice().sort((a, b) => {
      const aId = a['CoLD ID'] ?? a.ID ?? ''
      const bId = b['CoLD ID'] ?? b.ID ?? ''
      return aId.localeCompare(bId)
    })

    // Build a lookup for each level
    const idsByLevel = {}
    for (const item of sorted) {
      const id = item['CoLD ID'] ?? item.ID
      const level = typeof id === 'string' ? id.match(/\./g)?.length || 0 : 0
      if (!idsByLevel[level]) idsByLevel[level] = []
      idsByLevel[level].push(id)
    }

    // Build a map from id to array index for quick lookup
    const idToIndex = {}
    sorted.forEach((item, idx) => {
      const id = item['CoLD ID'] ?? item.ID
      idToIndex[id] = idx
    })

    // Precompute children for each id
    const childrenMap = {}
    sorted.forEach((item, idx, arr) => {
      const id = item['CoLD ID'] ?? item.ID
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
      const id = item['CoLD ID'] ?? item.ID
      const level = typeof id === 'string' ? id.match(/\./g)?.length || 0 : 0
      let parentId = null
      if (level > 0) {
        for (let j = idx - 1; j >= 0; j--) {
          const prevId = arr[j]['CoLD ID'] ?? arr[j].ID
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

      const baseId = item['CoLD ID'] ?? item.ID
      const answerId = iso3 ? `${iso3}_${baseId}` : baseId
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
        theme: item['Themes'],
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
