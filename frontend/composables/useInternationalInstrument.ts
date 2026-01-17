import { computed, type Ref } from "vue";
import { useRecordDetailsProcessed } from "@/composables/useRecordDetails";
import {
  type InternationalInstrumentResponse,
  type InternationalInstrument,
  processInternationalInstrument,
} from "@/types/entities/international-instrument";

export function useInternationalInstrument(id: Ref<string | number>) {
  return useRecordDetailsProcessed<InternationalInstrumentResponse, InternationalInstrument>(
    computed(() => "International Instruments"),
    id,
    processInternationalInstrument,
  );
}
