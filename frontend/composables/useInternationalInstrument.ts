import { computed, type Ref } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import {
  type InternationalInstrumentResponse,
  type InternationalInstrument,
  processInternationalInstrument,
} from "@/types/entities/international-instrument";

export function useInternationalInstrument(id: Ref<string | number>) {
  return useRecordDetails<
    InternationalInstrumentResponse,
    InternationalInstrument
  >(
    computed(() => "International Instruments"),
    id,
    processInternationalInstrument,
  );
}
