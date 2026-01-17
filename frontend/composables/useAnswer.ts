import { computed, type Ref } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import type { QuestionResponse } from "@/types/entities/question";

export function useAnswer(answerId: Ref<string | number>) {
  return useRecordDetails<QuestionResponse>(
    computed(() => "Answers"),
    answerId,
  );
}
