import { computed, type Ref } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import type { LiteratureResponse } from "@/types/entities/literature";

export function useLiterature(id: Ref<string | number>) {
  return useRecordDetails<LiteratureResponse>(
    computed(() => "Literature"),
    id,
  );
}
