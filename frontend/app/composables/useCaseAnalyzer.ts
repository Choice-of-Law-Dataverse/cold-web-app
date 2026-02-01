import { ref, type Ref, type ComputedRef } from "vue";
import type {
  JurisdictionInfo,
  AnalysisStepPayload,
  EditedAnalysisValues,
  SubmitForApprovalResponse,
  AnalysisStep,
} from "~/types/analyzer";
import {
  buildCaseAnalyzerPayload,
  extractErrorMessage,
} from "~/utils/analyzerPayloadParser";
import { streamSSE, type SSEEvent } from "~/composables/useSSEStream";

export interface DraftRecoveryData {
  draftId: number;
  status: string;
  fileName: string | null;
  jurisdictionInfo: JurisdictionInfo | null;
  analyzerData: Record<string, AnalysisStepPayload>;
}

const stepLabels: Record<string, string> = {
  col_extraction: "Choice of Law Extraction",
  theme_classification: "Theme Classification",
  case_citation: "Case Citation",
  relevant_facts: "Relevant Facts",
  pil_provisions: "PIL Provisions",
  col_issue: "Choice of Law Issue",
  courts_position: "Court's Position",
  obiter_dicta: "Obiter Dicta",
  dissenting_opinions: "Dissenting Opinions",
  abstract: "Abstract",
};

export function useCaseAnalyzer(
  analysisSteps: Ref<AnalysisStep[]>,
  stepsMap: ComputedRef<Map<string, AnalysisStep>>,
  analysisResults: Ref<Record<string, AnalysisStepPayload>>,
  onStepUpdate?: (stepName: string, data: AnalysisStepPayload) => void,
) {
  const isAnalyzing = ref(false);
  const isSubmitting = ref(false);
  const isSubmitted = ref(false);
  const isRecovering = ref(false);
  const toast = useToast();

  async function startAnalysis(
    draftId: number,
    jurisdictionInfo: JurisdictionInfo,
    resume = false,
  ): Promise<{ success: boolean; error?: string }> {
    isAnalyzing.value = true;

    try {
      await streamSSE<AnalysisStepPayload>({
        url: "/api/proxy/case-analyzer/analyze",
        method: "POST",
        body: {
          draft_id: draftId,
          jurisdiction: jurisdictionInfo,
          resume,
        },
        stepLabels,
        onEvent: (event: SSEEvent<AnalysisStepPayload>) => {
          const step = stepsMap.value.get(event.step);
          if (step) {
            step.status = event.status;
            if (event.data) {
              step.confidence =
                (event.data.confidence as string | null) || null;
              step.reasoning = (event.data.reasoning as string | null) || null;
              analysisResults.value[event.step] = event.data;
              onStepUpdate?.(event.step, event.data);
            }
            if (event.error) {
              step.error = event.error;
            }
          }
        },
      });

      return { success: true };
    } catch (err: unknown) {
      console.error("Analysis failed:", err);
      // Mark any in_progress steps as error
      for (const step of analysisSteps.value) {
        if (step.status === "in_progress") {
          step.status = "error";
          step.error = "Analysis interrupted";
        }
      }
      const errorMessage =
        err instanceof Error
          ? err.message
          : "Analysis failed. Please try again.";
      return {
        success: false,
        error: errorMessage,
      };
    } finally {
      isAnalyzing.value = false;
    }
  }

  async function submitSuggestion(
    draftId: number,
    jurisdictionInfo: JurisdictionInfo | null,
    analysisResults: Record<string, AnalysisStepPayload>,
    editableForm: EditedAnalysisValues,
  ): Promise<{ success: boolean; error?: string; suggestionId?: number }> {
    isSubmitting.value = true;

    try {
      const submittedData = buildCaseAnalyzerPayload(
        { ...editableForm },
        jurisdictionInfo,
        analysisResults,
        draftId,
      );

      const response = await $fetch<SubmitForApprovalResponse>(
        "/api/proxy/case-analyzer/submit",
        {
          method: "POST",
          body: {
            draft_id: draftId,
            submitted_data: submittedData,
          },
        },
      );

      isSubmitted.value = true;
      toast.add({
        title: "Submission Successful",
        description: `Suggestion #${response.draft_id} has been submitted for review.`,
        color: "info",
        icon: "i-heroicons-check-circle",
        duration: 5000,
      });

      return { success: true, suggestionId: response.draft_id };
    } catch (err) {
      console.error("Suggestion submission failed:", err);
      return {
        success: false,
        error:
          extractErrorMessage(err) ||
          "Failed to submit the analyzer suggestion.",
      };
    } finally {
      isSubmitting.value = false;
    }
  }

  async function recoverDraft(
    draftIdParam: string,
  ): Promise<{ success: boolean; data?: DraftRecoveryData; error?: string }> {
    const draftIdNum = parseInt(draftIdParam, 10);
    if (isNaN(draftIdNum)) {
      return { success: false, error: "Invalid draft ID" };
    }

    isRecovering.value = true;

    try {
      const draft = await $fetch<{
        draft_id: number;
        status: string;
        file_name: string | null;
        pdf_url: string | null;
        jurisdiction_info: {
          precise_jurisdiction?: string;
          jurisdiction_code?: string;
          legal_system_type?: string;
          confidence?: string;
          reasoning?: string;
        } | null;
        analyzer_data: Record<string, AnalysisStepPayload>;
        case_citation: string | null;
      }>(`/api/proxy/case-analyzer/draft/${draftIdNum}`);

      // Restore analysis results (step hydration handled by caller)
      if (draft.analyzer_data && Object.keys(draft.analyzer_data).length > 0) {
        analysisResults.value = draft.analyzer_data;
      }

      // Build jurisdiction info object
      const jurisdictionInfo: JurisdictionInfo | null = draft.jurisdiction_info
        ? {
            precise_jurisdiction:
              draft.jurisdiction_info.precise_jurisdiction || "",
            jurisdiction_code: draft.jurisdiction_info.jurisdiction_code || "",
            legal_system_type: draft.jurisdiction_info.legal_system_type || "",
            confidence: draft.jurisdiction_info.confidence || "",
            reasoning: draft.jurisdiction_info.reasoning || "",
          }
        : null;

      return {
        success: true,
        data: {
          draftId: draft.draft_id,
          status: draft.status,
          fileName: draft.file_name,
          jurisdictionInfo,
          analyzerData: draft.analyzer_data,
        },
      };
    } catch (err: unknown) {
      const fetchError = err as {
        statusCode?: number;
        data?: { detail?: string };
      };

      let errorMessage: string;
      if (fetchError.statusCode === 400) {
        errorMessage =
          fetchError.data?.detail ||
          "This draft has already been submitted for review. Start a new analysis.";
      } else if (fetchError.statusCode === 403) {
        errorMessage = "You can only access your own drafts.";
      } else if (fetchError.statusCode === 404) {
        errorMessage = "Draft not found.";
      } else {
        errorMessage =
          err instanceof Error ? err.message : "Failed to recover draft";
      }

      return { success: false, error: errorMessage };
    } finally {
      isRecovering.value = false;
    }
  }

  function reset() {
    isAnalyzing.value = false;
    isSubmitting.value = false;
    isSubmitted.value = false;
    isRecovering.value = false;
  }

  return {
    isAnalyzing,
    isSubmitting,
    isSubmitted,
    isRecovering,
    startAnalysis,
    submitSuggestion,
    recoverDraft,
    reset,
  };
}
