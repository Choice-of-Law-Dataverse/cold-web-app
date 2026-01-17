import { computed, type Ref } from "vue";
import { useRecordDetailsProcessed } from "@/composables/useRecordDetails";
import {
  type DomesticInstrumentResponse,
  type DomesticInstrument,
  processDomesticInstrument,
} from "@/types/entities/domestic-instrument";

export function useDomesticInstrument(id: Ref<string | number>) {
  return useRecordDetailsProcessed<DomesticInstrumentResponse, DomesticInstrument>(
    computed(() => "Domestic Instruments"),
    id,
    processDomesticInstrument,
  );
}
