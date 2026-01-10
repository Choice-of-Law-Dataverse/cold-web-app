import { ref, type Ref } from "vue";
import type {
  JurisdictionInfo,
  AnalysisStepPayload,
  SuggestionResponse,
  EditedAnalysisValues,
} from "~/types/analyzer";
import {
  buildCaseAnalyzerPayload,
  extractErrorMessage,
} from "~/utils/analyzerPayloadParser";

interface AnalysisStep {
  name: string;
  status: "pending" | "in_progress" | "completed" | "error";
  confidence: string | null;
  reasoning: string | null;
  error: string | null;
}

// Step label mapping for toast notifications
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

export function useCaseAnalysis(
  analysisSteps: Ref<AnalysisStep[]>,
  analysisResults: Ref<Record<string, AnalysisStepPayload>>,
  onStepUpdate?: (stepName: string, data: AnalysisStepPayload) => void,
) {
  const isAnalyzing = ref(false);
  const isSubmitting = ref(false);
  const isSubmitted = ref(false);
  const toast = useToast();

  async function startAnalysis(
    correlationId: string,
    jurisdictionInfo: JurisdictionInfo,
    resume = false,
  ): Promise<{ success: boolean; error?: string }> {
    isAnalyzing.value = true;

    try {
      const response = await fetch("/api/proxy/case-analysis/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          correlation_id: correlationId,
          jurisdiction: jurisdictionInfo,
          resume,
        }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No response body");
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              const step = analysisSteps.value.find(
                (s) => s.name === data.step,
              );
              if (step) {
                const prevStatus = step.status;
                step.status = data.status;
                if (data.data) {
                  step.confidence = data.data.confidence || null;
                  step.reasoning = data.data.reasoning || null;
                  analysisResults.value[data.step] = data.data;
                  onStepUpdate?.(data.step, data.data);
                }
                if (data.error) {
                  step.error = data.error;
                }
                // Show toast when step completes
                if (data.status === "completed" && prevStatus !== "completed") {
                  toast.add({
                    title: stepLabels[data.step] || data.step,
                    description: "Completed",
                    color: "teal",
                    icon: "i-heroicons-check-circle",
                    timeout: 2000,
                  });
                }
              }
            } catch (e) {
              console.error("Failed to parse SSE data:", e);
            }
          }
        }
      }

      return { success: true };
    } catch (err: unknown) {
      console.error("Analysis failed:", err);
      return {
        success: false,
        error: "Analysis failed. Please try again.",
      };
    } finally {
      isAnalyzing.value = false;
    }
  }

  async function submitSuggestion(
    correlationId: string,
    jurisdictionInfo: JurisdictionInfo | null,
    analysisResults: Record<string, AnalysisStepPayload>,
    editableForm: EditedAnalysisValues,
  ): Promise<{ success: boolean; error?: string; suggestionId?: number }> {
    if (!correlationId) {
      return { success: false, error: "No analysis data available" };
    }

    isSubmitting.value = true;

    try {
      const suggestionPayload = buildCaseAnalyzerPayload(
        { ...editableForm },
        correlationId,
        jurisdictionInfo,
        analysisResults,
      );

      const response = await $fetch<SuggestionResponse>(
        "/api/proxy/suggestions/case-analyzer",
        {
          method: "POST",
          body: suggestionPayload,
          headers: {
            Source: "case-analyzer-ui",
          },
        },
      );

      isSubmitted.value = true;
      toast.add({
        title: "Submission Successful",
        description: `Suggestion #${response.id} has been submitted for review.`,
        color: "teal",
        icon: "i-heroicons-check-circle",
        timeout: 5000,
      });

      return { success: true, suggestionId: response.id };
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

  function reset() {
    isAnalyzing.value = false;
    isSubmitting.value = false;
    isSubmitted.value = false;
  }

  return {
    isAnalyzing,
    isSubmitting,
    isSubmitted,
    startAnalysis,
    submitSuggestion,
    reset,
  };
}
