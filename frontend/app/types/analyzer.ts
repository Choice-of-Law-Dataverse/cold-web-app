import type { SSEEventStatus } from "~/utils/sseStream";

export interface JurisdictionInfo {
  legal_system_type: string;
  precise_jurisdiction: string;
  jurisdiction_code: string;
  confidence: string;
  reasoning: string;
}

export interface JurisdictionOption {
  id?: number;
  name: string;
  label: string;
  avatar?: string;
  coldId?: string;
  answerCoverage?: number;
}

export interface EditedAnalysisValues {
  caseCitation: string;
  jurisdiction: string;
  choiceOfLawSections: string;
  themes: string;
  caseAbstract: string;
  caseRelevantFacts: string;
  casePILProvisions: string;
  caseChoiceofLawIssue: string;
  caseCourtsPosition: string;
  caseObiterDicta: string;
  caseDissentingOpinions: string;
}

export interface AnalyzerFieldConfig {
  label: string;
  keys: string[];
  nestedKeys?: string[];
  joinWith?: string;
}

export interface CaseAnalyzerSuggestionPayload {
  draft_id?: number;
  username?: string;
  user_email?: string;
  model?: string;
  case_citation?: string;
  case_title?: string;
  court_name?: string;
  jurisdiction?: string;
  decision_date?: string;
  source_url?: string;
  is_common_law?: boolean;
  ratio_decidendi?: string;
  obiter_dicta?: string;
  dissenting_opinions?: string;
  courts_position?: string;
  relevant_facts?: string;
  legal_provisions?: string;
  choice_of_law_issue?: string;
  choice_of_law_sections?: string;
  themes?: string;
  abstract?: string;
  notes?: string;
  raw_data?: string | Record<string, unknown>;
}

export interface StoredAnalyzerSnapshot {
  correlationId?: string;
  jurisdiction?: JurisdictionInfo;
  analysisResults?: Record<string, AnalysisStepPayload>;
  editedFields?: EditedAnalysisValues;
}

export interface AnalysisStep {
  name: string;
  label: string;
  status: SSEEventStatus;
  confidence: string | null;
  reasoning: string | null;
  error: string | null;
}

export type AnalysisStepPayload = Record<string, unknown>;

export const ANALYZER_FIELD_MAP: Record<
  keyof EditedAnalysisValues,
  AnalyzerFieldConfig
> = {
  caseCitation: {
    label: "Case Citation",
    keys: ["case_citation_edited", "case_citation"],
    nestedKeys: ["case_citation"],
  },
  jurisdiction: {
    label: "Jurisdiction",
    keys: ["jurisdiction_edited", "jurisdiction"],
    nestedKeys: ["precise_jurisdiction"],
  },
  choiceOfLawSections: {
    label: "Choice of Law Sections",
    keys: ["col_sections_edited", "col_sections"],
    nestedKeys: ["col_sections"],
  },
  themes: {
    label: "Themes",
    keys: ["themes_edited", "themes"],
    nestedKeys: ["themes"],
    joinWith: ", ",
  },
  caseAbstract: {
    label: "Abstract",
    keys: ["abstract_edited", "abstract"],
    nestedKeys: ["abstract"],
  },
  caseRelevantFacts: {
    label: "Relevant Facts",
    keys: ["relevant_facts_edited", "relevant_facts"],
    nestedKeys: ["relevant_facts"],
  },
  casePILProvisions: {
    label: "PIL Provisions",
    keys: ["legal_provisions_edited", "legal_provisions", "pil_provisions"],
    nestedKeys: ["legal_provisions", "pil_provisions"],
    joinWith: ", ",
  },
  caseChoiceofLawIssue: {
    label: "Choice of Law Issue",
    keys: ["choice_of_law_issue_edited", "choice_of_law_issue", "col_issue"],
    nestedKeys: ["choice_of_law_issue", "col_issue"],
  },
  caseCourtsPosition: {
    label: "Court's Position",
    keys: ["courts_position_edited", "courts_position"],
    nestedKeys: ["courts_position"],
  },
  caseObiterDicta: {
    label: "Obiter Dicta",
    keys: ["obiter_dicta_edited", "obiter_dicta"],
    nestedKeys: ["obiter_dicta"],
  },
  caseDissentingOpinions: {
    label: "Dissenting Opinions",
    keys: ["dissenting_opinions_edited", "dissenting_opinions"],
    nestedKeys: ["dissenting_opinions"],
  },
};

/**
 * The analysis step that produces each form field, and the key holding the
 * field's value in that step's result. The jurisdiction field comes from
 * jurisdiction detection instead.
 */
export const ANALYZER_FIELD_SOURCES = {
  caseCitation: { step: "case_citation", key: "case_citation" },
  choiceOfLawSections: { step: "col_extraction", key: "col_sections" },
  themes: { step: "theme_classification", key: "themes" },
  caseAbstract: { step: "abstract", key: "abstract" },
  caseRelevantFacts: { step: "relevant_facts", key: "relevant_facts" },
  casePILProvisions: { step: "pil_provisions", key: "pil_provisions" },
  caseChoiceofLawIssue: { step: "col_issue", key: "col_issue" },
  caseCourtsPosition: { step: "courts_position", key: "courts_position" },
  caseObiterDicta: { step: "obiter_dicta", key: "obiter_dicta" },
  caseDissentingOpinions: {
    step: "dissenting_opinions",
    key: "dissenting_opinions",
  },
} as const satisfies Record<
  Exclude<keyof EditedAnalysisValues, "jurisdiction">,
  { step: string; key: string }
>;

export type AnalyzerResultField = keyof typeof ANALYZER_FIELD_SOURCES;

export const ANALYZER_RESULT_FIELDS = Object.keys(
  ANALYZER_FIELD_SOURCES,
) as AnalyzerResultField[];

/** Steps whose results feed the form, in no particular order. */
export const ANALYSIS_STEP_KEYS = ANALYZER_RESULT_FIELDS.map(
  (field) => ANALYZER_FIELD_SOURCES[field].step,
);

export function emptyAnalyzerValues(): EditedAnalysisValues {
  return {
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
}
