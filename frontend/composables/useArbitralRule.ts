import { computed, type Ref } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import {
  type ArbitralRuleResponse,
  type ArbitralRule,
  processArbitralRule,
} from "@/types/entities/arbitral-rule";

export function useArbitralRule(id: Ref<string | number>) {
  return useRecordDetails<ArbitralRuleResponse, ArbitralRule>(
    computed(() => "Arbitral Rules"),
    id,
    processArbitralRule,
  );
}
