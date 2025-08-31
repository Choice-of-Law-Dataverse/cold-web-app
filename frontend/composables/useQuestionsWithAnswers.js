import { ref, computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { questionConfig } from '~/config/pageConfigs'

const buildCompositeId = (jurisdiction, rawColdId, rawQuestionId) => {
  // If rawColdId already contains a jurisdiction prefix (ABC_), keep it.
  // Otherwise, build a composite with jurisdiction if available.
  if (rawColdId && /^[A-Z]{3}_/.test(rawColdId)) {
    return rawColdId
  } else if (jurisdiction && rawColdId) {
    return `${jurisdiction}_${rawColdId}`
  } else if (jurisdiction && rawQuestionId) {
    return `${jurisdiction}_${rawQuestionId}`
  } else {
    return rawColdId || rawQuestionId
  }
}

const processAnswerText = (answerText) => {
  if (typeof answerText === 'string' && answerText.includes(',')) {
    return answerText
      .split(',')
      .map((s) => s.trim())
      .join('; ')
  }
  return answerText
}

const buildChildrenMap = (sortedItems) => {
  const childrenMap = {}
  sortedItems.forEach((item, idx, arr) => {
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
  return childrenMap
}

const fetchAnswersData = async (jurisdiction) => {
  const config = useRuntimeConfig()

  const payload = {
    table: 'Answers',
    filters: [
      {
        column: 'Jurisdictions Alpha-3 code',
        value: jurisdiction?.toUpperCase(),
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

      const compositeId = buildCompositeId(
        jurisdiction,
        rawColdId,
        rawQuestionId
      )

      // Store under composite ID
      if (compositeId) map[compositeId] = answerValue
      // Also store under base ID (without jurisdiction) for any legacy lookups
      if (rawQuestionId && !map[rawQuestionId]) map[rawQuestionId] = answerValue
    }
  }
  return map
}

export function useQuestionsWithAnswers(jurisdiction) {
  const {
    data: questionsData,
    isLoading,
    error: questionsError,
  } = useQuestions(jurisdiction)

  const answersQuery = useQuery({
    queryKey: ['answers', jurisdiction],
    queryFn: () => fetchAnswersData(jurisdiction.value),
    enabled: computed(() => !!jurisdiction.value),
  })

  const data = computed(() => {
    if (!questionsData.value || !Array.isArray(questionsData.value)) return []

    const sorted = questionsData.value.slice().sort((a, b) => {
      const aId = a['CoLD ID'] ?? a.ID ?? ''
      const bId = b['CoLD ID'] ?? b.ID ?? ''
      return aId.localeCompare(bId)
    })

    const childrenMap = buildChildrenMap(sorted)

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

      const iso3 = jurisdiction?.value?.toUpperCase()
      const baseId = item['CoLD ID'] ?? item.ID
      const answerId = iso3 ? `${iso3}_${baseId}` : baseId
      const answerText = answersQuery.data.value?.[answerId] || ''
      const answerDisplay = processAnswerText(answerText)

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

  return {
    ...answersQuery,
    data,
    isLoading: computed(() => isLoading.value || answersQuery.isLoading.value),
    error: computed(() => questionsError.value || answersError.value),
  }
}
