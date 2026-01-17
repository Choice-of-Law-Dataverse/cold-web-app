import { computed, type Ref } from "vue";
import { useRecordDetailsProcessed } from "@/composables/useRecordDetails";
import {
  type RegionalInstrumentResponse,
  type RegionalInstrument,
  processRegionalInstrument,
} from "@/types/entities/regional-instrument";

export function useRegionalInstrument(id: Ref<string | number>) {
  return useRecordDetailsProcessed<RegionalInstrumentResponse, RegionalInstrument>(
    computed(() => "Regional Instruments"),
    id,
    processRegionalInstrument,
  );
}
