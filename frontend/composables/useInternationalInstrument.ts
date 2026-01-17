import { computed, type Ref } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import type { InternationalInstrumentResponse } from "@/types/entities/international-instrument";

export function useInternationalInstrument(id: Ref<string | number>) {
  return useRecordDetails<InternationalInstrumentResponse>(
    computed(() => "International Instruments"),
    id,
  );
}
