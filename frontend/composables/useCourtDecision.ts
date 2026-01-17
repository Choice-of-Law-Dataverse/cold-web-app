import { computed, type Ref } from "vue";
import { useRecordDetailsProcessed } from "@/composables/useRecordDetails";
import {
  type CourtDecisionResponse,
  type CourtDecision,
  processCourtDecision,
} from "@/types/entities/court-decision";

export function useCourtDecision(courtDecisionId: Ref<string | number>) {
  return useRecordDetailsProcessed<CourtDecisionResponse, CourtDecision>(
    computed(() => "Court Decisions"),
    courtDecisionId,
    processCourtDecision,
  );
}
