import { computed, type Ref } from "vue";
import {
  useRecordDetails,
  useRecordDetailsList,
} from "@/composables/useRecordDetails";

export function useAnswer(answerId: Ref<string | number>) {
  return useRecordDetails(
    computed(() => "Answers"),
    answerId,
  );
}

export function useAnswers(answerIds: Ref<(string | number)[]>) {
  return useRecordDetailsList(
    computed(() => "Answers"),
    answerIds,
  );
}
