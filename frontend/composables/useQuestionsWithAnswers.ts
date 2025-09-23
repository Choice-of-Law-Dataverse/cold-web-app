import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import type {
  FullTableRequest,
  QuestionItem,
  AnswerItem,
  QuestionWithAnswer,
} from '~/types/api'
import { useFullTable } from '@/composables/useFullTable'

const buildCompositeId = (
  jurisdiction: string,
  rawColdId: string,
  rawQuestionId: string
) => {
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

const processAnswerText = (answerText: string) => {
  if (typeof answerText === 'string' && answerText.includes(',')) {
    return answerText
      .split(',')
      .map((s) => s.trim())
      .join('; ')
  }
  return answerText
}

const buildChildrenMap = (sortedItems: QuestionItem[]) => {
  const childrenMap: Record<string, string[]> = {}
  sortedItems.forEach((item, idx, arr) => {
    const id = item['CoLD ID'] ?? item.ID
    const level = typeof id === 'string' ? id.match(/\./g)?.length || 0 : 0
    let parentId: string | null = null
    if (level > 0) {
      for (let j = idx - 1; j >= 0; j--) {
        const prevId = arr[j]['CoLD ID'] ?? arr[j].ID
        const prevLevel =
          typeof prevId === 'string' ? prevId.match(/\./g)?.length || 0 : 0
        if (prevLevel === level - 1) {
          parentId = prevId as string
          break
        }
      }
    }
    if (parentId && typeof id === 'string') {
      if (!childrenMap[parentId]) childrenMap[parentId] = []
      childrenMap[parentId].push(id)
    }
  })
  return childrenMap
}

const fetchAnswersData = async (jurisdiction: string) => {
  const { apiClient } = useApiClient()

  const body: FullTableRequest = {
    table: 'Answers',
    filters: [
      {
        column: 'Jurisdictions Alpha-3 code',
        value: jurisdiction?.toUpperCase(),
      },
    ],
  }

  const data = await apiClient('/search/full_table', { body })

  // Expect an array of answer rows. We construct the composite key
  // based on either existing 'CoLD ID' or by combining jurisdiction + question ID if needed.
  const map: Record<string, string> = {}
  if (Array.isArray(data)) {
    for (const row of data as AnswerItem[]) {
      const isoCode =
        (row['Jurisdictions Alpha-3 code'] as string) ||
        (row['Jurisdictions Alpha-3 Code'] as string) ||
        jurisdiction
      const rawQuestionId =
        row['Question ID'] || row['QuestionID'] || row['CoLD ID'] || row.ID
      const rawColdId = row['CoLD ID'] || row['Answer ID'] || rawQuestionId
      const answerValue = (row.Answer || row['Answer'] || '') as string

      const compositeId = buildCompositeId(
        isoCode,
        rawColdId as string,
        rawQuestionId as string
      )

      // Store under composite ID
      if (compositeId) map[compositeId] = answerValue
      // Also store under base ID (without jurisdiction) for any legacy lookups
      if (rawQuestionId && !map[rawQuestionId as string])
        map[rawQuestionId as string] = answerValue
    }
  }
  return map
}

export function useQuestionsWithAnswers(jurisdiction: Ref<string>) {
  const {
    data: questionsData,
    isLoading: questionsLoading,
    error: questionsError,
  } = useFullTable('Questions')

  const {
    data: answersData,
    isLoading: answersLoading,
    error: answersError,
  } = useQuery({
    queryKey: computed(() => ['answers', jurisdiction.value]),
    queryFn: () => fetchAnswersData(jurisdiction.value),
    enabled: computed(() => !!jurisdiction.value),
  })

  const data = computed((): QuestionWithAnswer[] => {
    if (!questionsData.value || !Array.isArray(questionsData.value)) return []

    const sorted = (questionsData.value as QuestionItem[])
      .slice()
      .sort((a, b) => {
        const aId = (a['CoLD ID'] ?? a.ID ?? '') as string
        const bId = (b['CoLD ID'] ?? b.ID ?? '') as string
        return aId.localeCompare(bId)
      })

    const childrenMap = buildChildrenMap(sorted)

    return sorted.map((item, idx, arr): QuestionWithAnswer => {
      const id = (item['CoLD ID'] ?? item.ID) as string
      const level = typeof id === 'string' ? id.match(/\./g)?.length || 0 : 0
      let parentId: string | null = null
      if (level > 0) {
        for (let j = idx - 1; j >= 0; j--) {
          const prevId = (arr[j]['CoLD ID'] ?? arr[j].ID) as string
          const prevLevel =
            typeof prevId === 'string' ? prevId.match(/\./g)?.length || 0 : 0
          if (prevLevel === level - 1) {
            parentId = prevId
            break
          }
        }
      }
      const hasExpand = !!childrenMap[id]

      const iso3 = jurisdiction?.value?.toUpperCase()
      const baseId = (item['CoLD ID'] ?? item.ID) as string
      const answerId = iso3 ? `${iso3}_${baseId}` : baseId
      const answerText = answersData?.value?.[answerId] || ''
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
    data,
    isLoading: computed(() => questionsLoading.value || answersLoading.value),
    error: computed(() => questionsError.value || answersError.value),
  }
}
