import { computed, type Ref } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import type { DomesticInstrumentResponse } from "@/types/entities/domestic-instrument";

export function useDomesticInstrument(id: Ref<string | number>) {
  return useRecordDetails<DomesticInstrumentResponse>(
    computed(() => "Domestic Instruments"),
    id,
  );
}
