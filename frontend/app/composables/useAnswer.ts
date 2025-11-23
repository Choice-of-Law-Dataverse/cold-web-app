import { computed, type Ref } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";

export function useAnswer(answerId: Ref<string | number>) {
  return useRecordDetails(
    computed(() => "Answers"),
    answerId,
  );
}
