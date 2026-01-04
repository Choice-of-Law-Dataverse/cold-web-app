import { reactive, computed, type Ref } from "vue";
import type {
  JurisdictionInfo,
  EditedAnalysisValues,
  AnalysisStepPayload,
} from "~/types/analyzer";

export function useAnalyzerForm(
  jurisdictionInfo: Ref<JurisdictionInfo | null>,
  analysisResults: Ref<Record<string, AnalysisStepPayload>>,
) {
  const editableForm = reactive<EditedAnalysisValues>({
    caseCitation: "",
    jurisdiction: "",
    caseAbstract: "",
    caseRelevantFacts: "",
    casePILProvisions: "",
    caseChoiceofLawIssue: "",
    caseCourtsPosition: "",
    caseObiterDicta: "",
    caseDissentingOpinions: "",
  });

  const isCommonLawJurisdiction = computed(() => {
    if (!jurisdictionInfo.value) return false;
    const legalSystem =
      jurisdictionInfo.value.legal_system_type?.toLowerCase() || "";
    const jurisdiction =
      jurisdictionInfo.value.precise_jurisdiction?.toLowerCase() || "";
    return legalSystem.includes("common-law") || jurisdiction === "india";
  });

  function getAnalysisValue(step: string, key: string): string {
    const payload = analysisResults.value[step];
    if (!payload || typeof payload !== "object") {
      return "";
    }
    const rawValue = (payload as AnalysisStepPayload)[key];
    return typeof rawValue === "string" ? rawValue : "";
  }

  function populateEditableForm() {
    if (
      !analysisResults.value ||
      Object.keys(analysisResults.value).length === 0
    ) {
      return;
    }
    editableForm.caseCitation = getAnalysisValue(
      "case_citation",
      "case_citation",
    );
    editableForm.caseAbstract = getAnalysisValue("abstract", "abstract");
    editableForm.caseRelevantFacts = getAnalysisValue(
      "relevant_facts",
      "relevant_facts",
    );
    editableForm.casePILProvisions = getAnalysisValue(
      "pil_provisions",
      "pil_provisions",
    );
    editableForm.caseChoiceofLawIssue = getAnalysisValue(
      "col_issue",
      "choice_of_law_issue",
    );
    editableForm.caseCourtsPosition = getAnalysisValue(
      "courts_position",
      "courts_position",
    );
    editableForm.caseObiterDicta = getAnalysisValue(
      "obiter_dicta",
      "obiter_dicta",
    );
    editableForm.caseDissentingOpinions = getAnalysisValue(
      "dissenting_opinions",
      "dissenting_opinions",
    );
    editableForm.jurisdiction =
      jurisdictionInfo.value?.precise_jurisdiction ?? "";
  }

  function resetEditableForm() {
    editableForm.caseCitation = "";
    editableForm.caseAbstract = "";
    editableForm.caseRelevantFacts = "";
    editableForm.casePILProvisions = "";
    editableForm.caseChoiceofLawIssue = "";
    editableForm.caseCourtsPosition = "";
    editableForm.caseObiterDicta = "";
    editableForm.caseDissentingOpinions = "";
    editableForm.jurisdiction = "";
  }

  return {
    editableForm,
    isCommonLawJurisdiction,
    populateEditableForm,
    resetEditableForm,
  };
}
