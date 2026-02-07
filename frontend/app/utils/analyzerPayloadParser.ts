import type {
  CaseAnalyzerSuggestionPayload,
  EditedAnalysisValues,
  AnalysisStepPayload,
  StoredAnalyzerSnapshot,
} from "~/types/analyzer";
import { ANALYZER_FIELD_MAP, ANALYSIS_STEP_KEYS } from "~/types/analyzer";

export function extractStringFromPayload(
  payload: Record<string, unknown>,
  keys: string[],
  preferredNestedKeys: string[],
  joinWith?: string,
): string | undefined {
  for (const key of keys) {
    const value = payload[key];
    const text = coerceValueToString(value, preferredNestedKeys, joinWith);
    if (text) {
      return text;
    }
  }
  return undefined;
}

export function coerceValueToString(
  value: unknown,
  preferredNestedKeys: string[] = [],
  joinWith = "\n",
): string | undefined {
  if (value === null || value === undefined) {
    return undefined;
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    return trimmed.length ? trimmed : undefined;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  if (Array.isArray(value)) {
    const joined = value
      .map(
        (entry) =>
          coerceValueToString(entry, preferredNestedKeys, joinWith) || "",
      )
      .filter((entry) => entry.length > 0)
      .join(joinWith);
    const trimmed = joined.trim();
    return trimmed.length ? trimmed : undefined;
  }
  if (typeof value === "object") {
    const obj = value as Record<string, unknown>;
    for (const key of preferredNestedKeys) {
      const nested = obj[key];
      if (typeof nested === "string" && nested.trim().length) {
        return nested.trim();
      }
      if (Array.isArray(nested)) {
        const result = coerceValueToString(
          nested,
          preferredNestedKeys,
          joinWith,
        );
        if (result) return result;
      }
    }
    const fallbackKeys = [
      "text",
      "value",
      "content",
      "summary",
      "description",
      "abstract",
      "case_citation",
      "choice_of_law_issue",
      "courts_position",
      "relevant_facts",
      "legal_provisions",
      "pil_provisions",
    ];
    for (const key of fallbackKeys) {
      const nested = obj[key];
      if (typeof nested === "string" && nested.trim().length) {
        return nested.trim();
      }
      if (Array.isArray(nested)) {
        const result = coerceValueToString(
          nested,
          preferredNestedKeys,
          joinWith,
        );
        if (result) return result;
      }
    }
    try {
      const json = JSON.stringify(obj, null, 2);
      const trimmed = json.trim();
      return trimmed.length ? trimmed : undefined;
    } catch {
      return undefined;
    }
  }
  return undefined;
}

export function getSnapshotSource(
  payload: Partial<CaseAnalyzerSuggestionPayload> & Record<string, unknown>,
): unknown {
  if (payload.raw_data) {
    return payload.raw_data;
  }
  if ((payload as Record<string, unknown>).rawData) {
    return (payload as Record<string, unknown>).rawData;
  }
  if ((payload as Record<string, unknown>).analyzer_snapshot) {
    return (payload as Record<string, unknown>).analyzer_snapshot;
  }
  return null;
}

export function parseRawAnalyzerSnapshot(
  raw: unknown,
): StoredAnalyzerSnapshot | null {
  if (!raw) {
    return null;
  }
  if (typeof raw === "string") {
    try {
      return JSON.parse(raw) as StoredAnalyzerSnapshot;
    } catch {
      return null;
    }
  }
  if (typeof raw === "object") {
    return raw as StoredAnalyzerSnapshot;
  }
  return null;
}

export function extractEditedFieldsFromPayload(
  payload: Record<string, unknown>,
): EditedAnalysisValues | null {
  let found = false;
  const values: EditedAnalysisValues = {
    caseCitation: "",
    jurisdiction: "",
    choiceOfLawSections: "",
    themes: "",
    caseAbstract: "",
    caseRelevantFacts: "",
    casePILProvisions: "",
    caseChoiceofLawIssue: "",
    caseCourtsPosition: "",
    caseObiterDicta: "",
    caseDissentingOpinions: "",
  };

  for (const field of Object.keys(ANALYZER_FIELD_MAP) as Array<
    keyof EditedAnalysisValues
  >) {
    const config = ANALYZER_FIELD_MAP[field];
    const editedKeys = config.keys.filter((key) => key.endsWith("_edited"));
    const text = extractStringFromPayload(
      payload,
      editedKeys,
      config.nestedKeys ?? [],
      config.joinWith,
    );
    if (text) {
      values[field] = text;
      found = true;
    } else {
      values[field] = "";
    }
  }

  return found ? values : null;
}

export function extractAnalysisResultsFromPayload(
  payload: Record<string, unknown>,
): Record<string, AnalysisStepPayload> | null {
  const results: Record<string, AnalysisStepPayload> = {};
  let found = false;

  for (const key of ANALYSIS_STEP_KEYS) {
    const value = payload[key];
    if (value && typeof value === "object") {
      results[key] = value as AnalysisStepPayload;
      found = true;
    }
  }

  return found ? results : null;
}

export function buildEditedValuesFromPayload(
  payload: Record<string, unknown>,
): EditedAnalysisValues {
  const finalValues: Partial<EditedAnalysisValues> = {};
  for (const field of Object.keys(ANALYZER_FIELD_MAP) as Array<
    keyof EditedAnalysisValues
  >) {
    finalValues[field] = getAnalyzerFieldText(field, payload);
  }
  return finalValues as EditedAnalysisValues;
}

export function getAnalyzerFieldText(
  field: keyof EditedAnalysisValues,
  payload: Record<string, unknown>,
): string {
  const config = ANALYZER_FIELD_MAP[field];
  const text = extractStringFromPayload(
    payload,
    config.keys,
    config.nestedKeys ?? [],
    config.joinWith,
  );
  return text ?? "";
}

export function buildCaseAnalyzerPayload(
  editedPayload: EditedAnalysisValues,
  jurisdictionInfo: unknown,
  analysisResults: Record<string, AnalysisStepPayload>,
  draftId: number,
): CaseAnalyzerSuggestionPayload {
  const payload: CaseAnalyzerSuggestionPayload = {
    case_citation: sanitizeAnalyzerField(editedPayload.caseCitation),
    jurisdiction: sanitizeAnalyzerField(editedPayload.jurisdiction),
    choice_of_law_sections: sanitizeAnalyzerField(
      editedPayload.choiceOfLawSections,
    ),
    themes: sanitizeAnalyzerField(editedPayload.themes),
    abstract: sanitizeAnalyzerField(editedPayload.caseAbstract),
    relevant_facts: sanitizeAnalyzerField(editedPayload.caseRelevantFacts),
    legal_provisions: sanitizeAnalyzerField(editedPayload.casePILProvisions),
    choice_of_law_issue: sanitizeAnalyzerField(
      editedPayload.caseChoiceofLawIssue,
    ),
    courts_position: sanitizeAnalyzerField(editedPayload.caseCourtsPosition),
    obiter_dicta: sanitizeAnalyzerField(editedPayload.caseObiterDicta),
    dissenting_opinions: sanitizeAnalyzerField(
      editedPayload.caseDissentingOpinions,
    ),
    draft_id: draftId,
  };

  payload.raw_data = JSON.stringify({
    draftId,
    jurisdiction: jurisdictionInfo,
    analysisResults,
    editedFields: editedPayload,
  });

  return payload;
}

export function sanitizeAnalyzerField(
  value: string | null | undefined,
): string | undefined {
  if (!value) {
    return undefined;
  }
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
}

export function extractErrorMessage(err: unknown): string | null {
  if (err && typeof err === "object") {
    const data = (err as { data?: { detail?: unknown } }).data;
    if (data && typeof data === "object" && "detail" in data) {
      const detail = (data as { detail?: unknown }).detail;
      if (typeof detail === "string") {
        return detail;
      }
    }
    if (
      "message" in err &&
      typeof (err as { message?: unknown }).message === "string"
    ) {
      return (err as { message: string }).message;
    }
  }
  return null;
}
