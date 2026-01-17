import { computed, type Ref } from "vue";
import { useRecordDetailsProcessed } from "@/composables/useRecordDetails";
import {
  type QuestionResponse,
  type Question,
  processQuestion,
} from "@/types/entities/question";

export function useAnswer(answerId: Ref<string | number>) {
  return useRecordDetailsProcessed<QuestionResponse, Question>(
    computed(() => "Answers"),
    answerId,
    processQuestion,
  );
}
