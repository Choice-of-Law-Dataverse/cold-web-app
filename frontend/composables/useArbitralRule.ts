import { computed, type Ref } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import type { ArbitralRuleResponse } from "@/types/entities/arbitral-rule";

export function useArbitralRule(id: Ref<string | number>) {
  return useRecordDetails<ArbitralRuleResponse>(
    computed(() => "Arbitral Rules"),
    id,
  );
}
