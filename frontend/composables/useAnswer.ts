import { computed, type Ref } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import {
  type QuestionResponse,
  type Question,
  processQuestion,
} from "@/types/entities/question";

export function useAnswer(answerId: Ref<string | number>) {
  return useRecordDetails<QuestionResponse, Question>(
    computed(() => "Answers"),
    answerId,
    processQuestion,
  );
}
