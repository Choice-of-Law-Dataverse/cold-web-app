import { reactive, computed, type Ref } from "vue";
import {
  ANALYZER_FIELD_SOURCES,
  ANALYZER_RESULT_FIELDS,
  emptyAnalyzerValues,
  type JurisdictionInfo,
  type EditedAnalysisValues,
  type AnalysisStepPayload,
  type AnalyzerResultField,
} from "~/types/analyzer";

export function useAnalyzerForm(
  jurisdictionInfo: Ref<JurisdictionInfo | null>,
  analysisResults: Ref<Record<string, AnalysisStepPayload>>,
) {
  const editableForm = reactive<EditedAnalysisValues>(emptyAnalyzerValues());
  let lastFilled = emptyAnalyzerValues();

  const isCommonLawJurisdiction = computed(() => {
    if (!jurisdictionInfo.value) return false;
    const legalSystem =
      jurisdictionInfo.value.legal_system_type?.toLowerCase() || "";
    const jurisdiction =
      jurisdictionInfo.value.precise_jurisdiction?.toLowerCase() || "";
    return legalSystem.includes("common-law") || jurisdiction === "india";
  });

  function resultText(field: AnalyzerResultField): string {
    const { step, key } = ANALYZER_FIELD_SOURCES[field];
    const payload = analysisResults.value[step];
    if (!payload || typeof payload !== "object") return "";
    const rawValue = payload[key];
    if (typeof rawValue === "string") return rawValue;
    if (Array.isArray(rawValue)) return rawValue.join(", ");
    return "";
  }

  function fill(field: keyof EditedAnalysisValues, value: string) {
    if (editableForm[field] !== lastFilled[field]) return;
    editableForm[field] = value;
    lastFilled[field] = value;
  }

  /**
   * Copies the current analysis results into the form. A field whose value
   * no longer matches what was last filled in has been edited by the user
   * and is left alone, so results streaming in for later steps never
   * overwrite an edit.
   */
  function populateEditableForm() {
    for (const field of ANALYZER_RESULT_FIELDS) {
      fill(field, resultText(field));
    }
    fill("jurisdiction", jurisdictionInfo.value?.precise_jurisdiction ?? "");
  }

  /** Clears the form and forgets past edits, ready for a fresh analysis. */
  function resetEditableForm() {
    Object.assign(editableForm, emptyAnalyzerValues());
    lastFilled = emptyAnalyzerValues();
  }

  return {
    editableForm,
    isCommonLawJurisdiction,
    populateEditableForm,
    resetEditableForm,
  };
}
