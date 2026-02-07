import { ref, computed } from "vue";
import type {
  AnalysisStep,
  AnalysisStepPayload,
  EditedAnalysisValues,
  JurisdictionInfo,
} from "~/types/analyzer";
import type { SSEEventStatus } from "~/composables/useSSEStream";

export function useAnalysisSteps() {
  // Steps ordered by workflow dependency chain
  const analysisSteps = ref<AnalysisStep[]>([
    // Phase 1: Document processing
    {
      name: "document_upload",
      label: "Document Upload",
      status: "pending",
      confidence: null,
      reasoning: null,
      error: null,
    },
    {
      name: "jurisdiction_detection",
      label: "Jurisdiction Detection",
      status: "pending",
      confidence: null,
      reasoning: null,
      error: null,
    },
    // Phase 2: Initial extraction (depends on document)
    {
      name: "col_extraction",
      label: "Choice of Law Extraction",
      status: "pending",
      confidence: null,
      reasoning: null,
      error: null,
    },
    {
      name: "theme_classification",
      label: "Theme Classification",
      status: "pending",
      confidence: null,
      reasoning: null,
      error: null,
    },
    // Phase 3: Content extraction (depends on col_extraction)
    {
      name: "case_citation",
      label: "Case Citation",
      status: "pending",
      confidence: null,
      reasoning: null,
      error: null,
    },
    {
      name: "relevant_facts",
      label: "Relevant Facts",
      status: "pending",
      confidence: null,
      reasoning: null,
      error: null,
    },
    {
      name: "pil_provisions",
      label: "PIL Provisions",
      status: "pending",
      confidence: null,
      reasoning: null,
      error: null,
    },
    {
      name: "col_issue",
      label: "Choice of Law Issue",
      status: "pending",
      confidence: null,
      reasoning: null,
      error: null,
    },
    {
      name: "courts_position",
      label: "Court's Position",
      status: "pending",
      confidence: null,
      reasoning: null,
      error: null,
    },
    // Phase 4: Common law specific (depends on courts_position)
    {
      name: "obiter_dicta",
      label: "Obiter Dicta",
      status: "pending",
      confidence: null,
      reasoning: null,
      error: null,
    },
    {
      name: "dissenting_opinions",
      label: "Dissenting Opinions",
      status: "pending",
      confidence: null,
      reasoning: null,
      error: null,
    },
    // Phase 5: Summary (depends on all above)
    {
      name: "abstract",
      label: "Abstract",
      status: "pending",
      confidence: null,
      reasoning: null,
      error: null,
    },
  ]);

  const isAnalyzing = ref(false);

  // O(1) lookup map
  const stepsMap = computed(
    () => new Map(analysisSteps.value.map((s) => [s.name, s])),
  );

  const formFieldAnalysisStepMap: Record<string, string> = {
    caseCitation: "case_citation",
    choiceOfLawSections: "col_extraction",
    themes: "theme_classification",
    caseAbstract: "abstract",
    caseRelevantFacts: "relevant_facts",
    casePILProvisions: "pil_provisions",
    caseChoiceofLawIssue: "col_issue",
    caseCourtsPosition: "courts_position",
    caseObiterDicta: "obiter_dicta",
    caseDissentingOpinions: "dissenting_opinions",
  };

  function updateStepStatus(
    stepName: string,
    status: SSEEventStatus,
    data?: { confidence?: string; reasoning?: string },
  ) {
    const step = stepsMap.value.get(stepName);
    if (step) {
      step.status = status;
      if (data) {
        step.confidence = data.confidence || null;
        step.reasoning = data.reasoning || null;
      }
    }
  }

  /**
   * Maps upload SSE steps to analysis step tracker updates
   */
  function handleUploadStepChange(
    uploadStep: string | null,
    jurisdictionInfo?: JurisdictionInfo | null,
  ) {
    if (!uploadStep) return;

    if (
      uploadStep === "uploading_to_storage" ||
      uploadStep === "extracting_text"
    ) {
      updateStepStatus("document_upload", "in_progress");
    } else if (uploadStep === "detecting_jurisdiction") {
      updateStepStatus("document_upload", "completed");
      updateStepStatus("jurisdiction_detection", "in_progress");
    } else if (uploadStep === "upload_complete" && jurisdictionInfo) {
      updateStepStatus("jurisdiction_detection", "completed", {
        confidence: jurisdictionInfo.confidence,
        reasoning: jurisdictionInfo.reasoning,
      });
    }
  }

  function getFieldStatus(fieldName: keyof EditedAnalysisValues) {
    const stepName = formFieldAnalysisStepMap[fieldName];
    if (!stepName) return null;
    return stepsMap.value.get(stepName) || null;
  }

  function isFieldLoading(fieldName: keyof EditedAnalysisValues): boolean {
    const step = getFieldStatus(fieldName);
    return (
      step?.status === "in_progress" ||
      (isAnalyzing.value && step?.status === "pending")
    );
  }

  function isFieldDisabled(_fieldName: keyof EditedAnalysisValues): boolean {
    return isAnalyzing.value;
  }

  function hydrateAnalysisStepsFromResults(
    results: Record<string, AnalysisStepPayload>,
  ) {
    for (const step of analysisSteps.value) {
      const result = results[step.name];
      if (result) {
        step.status = "completed";
        step.confidence =
          typeof result.confidence === "string" ? result.confidence : null;
        step.reasoning =
          typeof result.reasoning === "string" ? result.reasoning : null;
        step.error = null;
      }
    }
  }

  function markStepsCompleteWithoutResults() {
    for (const step of analysisSteps.value) {
      if (step.status !== "error") {
        step.status = "completed";
        step.confidence = null;
        step.reasoning = null;
        step.error = null;
      }
    }
  }

  function resetAnalysisSteps(excludeSteps?: Set<string>) {
    for (const step of analysisSteps.value) {
      if (excludeSteps?.has(step.name)) continue;
      step.status = "pending";
      step.confidence = null;
      step.reasoning = null;
      step.error = null;
    }
  }

  function getConfidenceColor(
    confidence: string,
  ): "success" | "warning" | "error" | "neutral" {
    switch (confidence) {
      case "high":
        return "success";
      case "medium":
        return "warning";
      case "low":
        return "error";
      default:
        return "neutral";
    }
  }

  return {
    analysisSteps,
    stepsMap,
    isAnalyzing,
    updateStepStatus,
    handleUploadStepChange,
    getFieldStatus,
    isFieldLoading,
    isFieldDisabled,
    hydrateAnalysisStepsFromResults,
    markStepsCompleteWithoutResults,
    resetAnalysisSteps,
    getConfidenceColor,
  };
}
