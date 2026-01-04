import { ref } from "vue";
import type {
  AnalysisStep,
  AnalysisStepPayload,
  EditedAnalysisValues,
} from "~/types/analyzer";

export function useAnalysisSteps() {
  const analysisSteps = ref<AnalysisStep[]>([
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
    {
      name: "case_citation",
      label: "Case Citation",
      status: "pending",
      confidence: null,
      reasoning: null,
      error: null,
    },
    {
      name: "abstract",
      label: "Abstract Generation",
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
  ]);

  const isAnalyzing = ref(false);

  const formFieldAnalysisStepMap: Record<string, string> = {
    caseCitation: "case_citation",
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
        step.status = "completed";
        step.confidence =
          typeof result.confidence === "string"
            ? (result.confidence as string)
            : step.confidence;
        step.reasoning =
          typeof result.reasoning === "string"
            ? (result.reasoning as string)
            : step.reasoning;
        step.error = null;
      } else if (step.status !== "error") {
        step.status = "completed";
        step.confidence = null;
        step.reasoning = null;
        step.error = null;
      }
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
  ): "green" | "yellow" | "red" | "gray" {
    switch (confidence) {
      case "high":
        return "green";
      case "medium":
        return "yellow";
      case "low":
        return "red";
      default:
        return "gray";
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
