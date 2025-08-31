import { computed } from 'vue'
import { useQueries } from '@tanstack/vue-query'

const fetchQuestionLabel = async (jurisdictionCode, questionId) => {
  const config = useRuntimeConfig()

  const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
    method: 'POST',
    headers: {
      authorization: `Bearer ${config.public.FASTAPI}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      table: 'Answers',
      id: `${jurisdictionCode}_${questionId}`,
    }),
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch question label: ${response.statusText}`)
  }

  const data = await response.json()

  // Check if the API returned an error response
  if (data.error) {
    throw new Error(data.error)
  }

  return data.Question || `${jurisdictionCode}_${questionId}`
}

export function useRelatedQuestions(jurisdictionCode, questions) {
  const questionList = computed(() =>
    questions.value
      ? questions.value
          .split(',')
          .map((q) => q.trim())
          .filter((q) => q)
      : []
  )

  const queries = computed(() => {
    if (!jurisdictionCode.value || !questionList.value.length) {
      return []
    }

    return questionList.value.map((questionId) => ({
      queryKey: ['questionLabel', jurisdictionCode.value, questionId],
      queryFn: () => fetchQuestionLabel(jurisdictionCode.value, questionId),
      enabled: !!jurisdictionCode.value && !!questionId,
    }))
  })

  const results = useQueries({
    queries: queries,
  })

  const questionLabels = computed(() => {
    return results.value.map((result) => {
      if (result.data) {
        return result.data
      }
      // Fallback to the original format if query failed
      const questionIndex = results.value.indexOf(result)
      return questionList.value[questionIndex]
        ? `${jurisdictionCode.value}_${questionList.value[questionIndex]}`
        : ''
    })
  })

  const isLoading = computed(() => {
    return results.value.some((result) => result.isLoading)
  })

  const hasError = computed(() => {
    return results.value.some((result) => result.isError)
  })

  return {
    questionList,
    questionLabels,
    isLoading,
    hasError,
    results,
  }
}
