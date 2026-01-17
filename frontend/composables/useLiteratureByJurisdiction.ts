import { ref, type Ref } from "vue";
import { useFullTable } from "@/composables/useFullTable";
import type { LiteratureResponse } from "@/types/entities/literature";

export function useLiteratureByJurisdiction(jurisdiction: Ref<string>) {
  if (!jurisdiction.value) {
    return { data: ref<LiteratureResponse[]>([]), isLoading: ref(false) };
  }

  return useFullTable<LiteratureResponse>("Literature", {
    filters: [
      {
        column: "Jurisdiction",
        value: jurisdiction.value,
      },
    ],
  });
}
