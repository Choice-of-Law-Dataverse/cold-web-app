import { computed, type Ref } from 'vue'
import {
  useRecordDetails,
  useRecordDetailsList,
} from '@/composables/useRecordDetails'

type Options = {
  enableErrorHandling?: boolean
  redirectOnNotFound?: boolean
  showToast?: boolean
  select?: (data: any) => any
}

export function useAnswer(
  answerId: Ref<string | number>,
  options: Options = {}
) {
  return useRecordDetails(
    computed(() => 'Answers'),
    answerId,
    options
  )
}

export function useAnswers(
  answerIds: Ref<(string | number)[]>,
  options: Options = {}
) {
  return useRecordDetailsList(
    computed(() => 'Answers'),
    answerIds,
    options
  )
}
