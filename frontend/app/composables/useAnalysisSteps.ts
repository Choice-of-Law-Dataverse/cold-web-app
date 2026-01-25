import { ref } from "vue";
import type {
  AnalysisStep,
  AnalysisStepPayload,
  EditedAnalysisValues,
} from "~/types/analyzer";

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

  function getFieldStatus(fieldName: keyof EditedAnalysisValues) {
    const stepName = formFieldAnalysisStepMap[fieldName];
    const step = analysisSteps.value.find((s) => s.name === stepName);
    return step || null;
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
    analysisSteps.value.forEach((step) => {
      const result = results[step.name];
      if (result) {
        // Only mark as completed if we have actual result data
        step.status = "completed";
        step.confidence =
          typeof result.confidence === "string"
            ? (result.confidence as string)
            : null;
        step.reasoning =
          typeof result.reasoning === "string"
            ? (result.reasoning as string)
            : null;
        step.error = null;
      }
      // Steps without results stay in their current state (pending)
      // Don't mark them as completed - they weren't executed
    });
  }

  function markStepsCompleteWithoutResults() {
    analysisSteps.value.forEach((step) => {
      if (step.status !== "error") {
        step.status = "completed";
        step.confidence = null;
        step.reasoning = null;
        step.error = null;
      }
    });
  }

  function resetAnalysisSteps() {
    analysisSteps.value.forEach((step) => {
      step.status = "pending";
      step.confidence = null;
      step.reasoning = null;
      step.error = null;
    });
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
    isAnalyzing,
    getFieldStatus,
    isFieldLoading,
    isFieldDisabled,
    hydrateAnalysisStepsFromResults,
    markStepsCompleteWithoutResults,
    resetAnalysisSteps,
    getConfidenceColor,
  };
}
