import { ref, type Ref } from "vue";
import type {
  JurisdictionInfo,
  EditedAnalysisValues,
  AnalysisStepPayload,
  CaseAnalyzerSuggestionRecord,
  CaseAnalyzerSuggestionPayload,
} from "~/types/analyzer";
import {
  extractEditedFieldsFromPayload,
  extractAnalysisResultsFromPayload,
  parseRawAnalyzerSnapshot,
  getSnapshotSource,
  buildEditedValuesFromPayload as buildEditedValuesFromPayloadUtil,
} from "~/utils/analyzerPayloadParser";

export function useAnalyzerStorage(
  correlationId: Ref<string | null>,
  jurisdictionInfo: Ref<JurisdictionInfo | null>,
  analysisResults: Ref<Record<string, AnalysisStepPayload>>,
  editableForm: EditedAnalysisValues,
  hydrateAnalysisStepsFromResults: (
    results: Record<string, AnalysisStepPayload>,
  ) => void,
  markStepsCompleteWithoutResults: () => void,
) {
  const suggestionId = ref<number | null>(null);
  const lastFetchedSuggestionId = ref<number | null>(null);
  const isLoadingExistingSuggestion = ref(false);
  const draftSavedMessage = ref<string | null>(null);

  function storeAnalysisResults(editedValues?: EditedAnalysisValues) {
    if (typeof window === "undefined") {
      return;
    }

    const payload: Record<string, unknown> = {
      correlationId: correlationId.value,
      jurisdiction: jurisdictionInfo.value,
      results: analysisResults.value,
    };

    if (editedValues || editableForm) {
      payload.edited = editedValues ?? { ...editableForm };
    }

    sessionStorage.setItem("caseAnalysisResults", JSON.stringify(payload));
  }

  async function saveEditedDraft(isSavingDraft: Ref<boolean>) {
    isSavingDraft.value = true;
    try {
      storeAnalysisResults();
      draftSavedMessage.value = new Date().toLocaleTimeString();
    } finally {
      isSavingDraft.value = false;
    }
  }

  async function fetchCaseAnalyzerSuggestion(
    id: number,
    options: { syncQuery?: boolean; silent?: boolean } = {},
    updateSuggestionIdFn: (
      id: number,
      options?: { syncQuery?: boolean },
    ) => void,
    setError: (error: string) => void,
    extractErrorMessage: (err: unknown) => string | null,
  ): Promise<string | null> {
    if (!Number.isFinite(id)) {
      return null;
    }

    isLoadingExistingSuggestion.value = true;

    try {
      const record = await $fetch<CaseAnalyzerSuggestionRecord>(
        `/api/proxy/suggestions/case-analyzer/${id}`,
      );
      lastFetchedSuggestionId.value = id;
      updateSuggestionIdFn(id, { syncQuery: options.syncQuery !== false });
      if (record.payload) {
        applySuggestionRecord(record.payload);
      }
      if (!options.silent) {
        return `Loaded suggestion #${id} from database.`;
      }
      return null;
    } catch (err) {
      console.error("Failed to load suggestion:", err);
      setError(extractErrorMessage(err) || `Unable to load suggestion #${id}.`);
      return null;
    } finally {
      isLoadingExistingSuggestion.value = false;
    }
  }

  function applySuggestionRecord(payload: Record<string, unknown>) {
    const typedPayload = payload as Record<string, unknown> &
      Partial<CaseAnalyzerSuggestionPayload>;

    const snapshotSource = getSnapshotSource(typedPayload);
    const snapshot = parseRawAnalyzerSnapshot(snapshotSource);
    const legacyEditedFields = extractEditedFieldsFromPayload(typedPayload);

    if (snapshot?.editedFields) {
      Object.assign(editableForm, snapshot.editedFields);
    } else if (legacyEditedFields) {
      Object.assign(editableForm, legacyEditedFields);
    } else {
      Object.assign(
        editableForm,
        buildEditedValuesFromPayloadUtil(typedPayload),
      );
    }

    if (snapshot?.correlationId) {
      correlationId.value = snapshot.correlationId;
    } else if (typeof typedPayload.correlation_id === "string") {
      correlationId.value = typedPayload.correlation_id as string;
    }

    if (snapshot?.jurisdiction) {
      jurisdictionInfo.value = snapshot.jurisdiction;
    } else if (
      typeof typedPayload.jurisdiction === "string" &&
      typedPayload.jurisdiction.trim()
    ) {
      jurisdictionInfo.value = buildFallbackJurisdiction(
        typedPayload.jurisdiction,
      );
    }

    const resolvedAnalysisResults =
      snapshot?.analysisResults ??
      extractAnalysisResultsFromPayload(typedPayload);

    if (resolvedAnalysisResults) {
      analysisResults.value = resolvedAnalysisResults;
      hydrateAnalysisStepsFromResults(resolvedAnalysisResults);
    } else {
      analysisResults.value = {};
      markStepsCompleteWithoutResults();
    }

    draftSavedMessage.value = null;
    storeAnalysisResults();
  }

  function buildFallbackJurisdiction(label: string): JurisdictionInfo {
    return {
      legal_system_type: "Unknown",
      precise_jurisdiction: label,
      jurisdiction_code: "",
      confidence: "low",
      reasoning: "Loaded from saved suggestion",
    };
  }

  function parseSuggestionIdParam(value: unknown): number | null {
    if (Array.isArray(value)) {
      return parseSuggestionIdParam(value[0]);
    }
    if (typeof value === "string") {
      const parsed = Number.parseInt(value, 10);
      return Number.isFinite(parsed) ? parsed : null;
    }
    if (typeof value === "number" && Number.isFinite(value)) {
      return value;
    }
    return null;
  }

  return {
    suggestionId,
    lastFetchedSuggestionId,
    isLoadingExistingSuggestion,
    draftSavedMessage,
    storeAnalysisResults,
    saveEditedDraft,
    fetchCaseAnalyzerSuggestion,
    parseSuggestionIdParam,
    applySuggestionRecord,
  };
}
