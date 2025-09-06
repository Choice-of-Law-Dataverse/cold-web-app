import { computed } from 'vue'
import { useQueries } from '@tanstack/vue-query'
import { useApiClient } from '@/composables/useApiClient'
import type { DetailsByIdRequest } from '~/types/api'

const fetchQuestionLabel = async (
  jurisdictionCode: string,
  questionId: string
) => {
  const { apiClient } = useApiClient()

  const body: DetailsByIdRequest = {
    table: 'Answers',
    id: `${jurisdictionCode}_${questionId}`,
  }

  const data = await apiClient('/search/details', { body })

  return data.Question || `${jurisdictionCode}_${questionId}`
}

export function useRelatedQuestions(
  jurisdictionCode: Ref<string>,
  questions: Ref<string>
) {
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
