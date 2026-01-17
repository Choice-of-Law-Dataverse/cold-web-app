import { computed, type Ref } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import {
  type RegionalInstrumentResponse,
  type RegionalInstrument,
  processRegionalInstrument,
} from "@/types/entities/regional-instrument";

export function useRegionalInstrument(id: Ref<string | number>) {
  return useRecordDetails<RegionalInstrumentResponse, RegionalInstrument>(
    computed(() => "Regional Instruments"),
    id,
    processRegionalInstrument,
  );
}
