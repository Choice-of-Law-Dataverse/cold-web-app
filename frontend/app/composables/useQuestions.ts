import { useFullTable } from "@/composables/useFullTable";

export function useQuestions() {
  return useFullTable("Questions");
}
