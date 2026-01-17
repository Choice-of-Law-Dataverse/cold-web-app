import { computed, type Ref } from "vue";
import { useRecordDetailsProcessed } from "@/composables/useRecordDetails";
import {
  type ArbitralAwardResponse,
  type ArbitralAward,
  processArbitralAward,
} from "@/types/entities/arbitral-award";

export function useArbitralAward(id: Ref<string | number>) {
  return useRecordDetailsProcessed<ArbitralAwardResponse, ArbitralAward>(
    computed(() => "Arbitral Awards"),
    id,
    processArbitralAward,
  );
}
