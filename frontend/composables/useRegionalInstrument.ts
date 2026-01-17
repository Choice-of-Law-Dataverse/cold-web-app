import { computed, type Ref } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import type { RegionalInstrumentResponse } from "@/types/entities/regional-instrument";

export function useRegionalInstrument(id: Ref<string | number>) {
  return useRecordDetails<RegionalInstrumentResponse>(
    computed(() => "Regional Instruments"),
    id,
  );
}
