import { computed, type Ref } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import type { ArbitralAwardResponse } from "@/types/entities/arbitral-award";

export function useArbitralAward(id: Ref<string | number>) {
  return useRecordDetails<ArbitralAwardResponse>(
    computed(() => "Arbitral Awards"),
    id,
  );
}
