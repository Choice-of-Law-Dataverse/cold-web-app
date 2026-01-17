import { computed, type Ref } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import {
  type CourtDecisionResponse,
  type CourtDecision,
  processCourtDecision,
} from "@/types/entities/court-decision";

export function useCourtDecision(courtDecisionId: Ref<string | number>) {
  return useRecordDetails<CourtDecisionResponse, CourtDecision>(
    computed(() => "Court Decisions"),
    courtDecisionId,
    processCourtDecision,
  );
}
