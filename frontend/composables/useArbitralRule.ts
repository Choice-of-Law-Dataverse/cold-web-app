import { computed, type Ref } from "vue";
import { useRecordDetailsProcessed } from "@/composables/useRecordDetails";
import {
  type ArbitralRuleResponse,
  type ArbitralRule,
  processArbitralRule,
} from "@/types/entities/arbitral-rule";

export function useArbitralRule(id: Ref<string | number>) {
  return useRecordDetailsProcessed<ArbitralRuleResponse, ArbitralRule>(
    computed(() => "Arbitral Rules"),
    id,
    processArbitralRule,
  );
}
