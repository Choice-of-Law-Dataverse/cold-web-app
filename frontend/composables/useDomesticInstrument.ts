import { computed, type Ref } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import {
  type DomesticInstrumentResponse,
  type DomesticInstrument,
  processDomesticInstrument,
} from "@/types/entities/domestic-instrument";

export function useDomesticInstrument(id: Ref<string | number>) {
  return useRecordDetails<DomesticInstrumentResponse, DomesticInstrument>(
    computed(() => "Domestic Instruments"),
    id,
    processDomesticInstrument,
  );
}
