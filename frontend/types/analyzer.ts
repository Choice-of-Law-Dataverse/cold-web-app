export interface JurisdictionInfo {
  legal_system_type: string;
  precise_jurisdiction: string;
  jurisdiction_code: string;
  confidence: string;
  reasoning: string;
}

export interface JurisdictionOption {
  label: string;
  avatar?: string;
  alpha3Code?: string;
  answerCoverage?: number;
}

export interface EditedAnalysisValues {
  caseCitation: string;
  jurisdiction: string;
  caseAbstract: string;
  caseRelevantFacts: string;
  casePILProvisions: string;
  caseChoiceofLawIssue: string;
  caseCourtsPosition: string;
  caseObiterDicta: string;
  caseDissentingOpinions: string;
}

export interface AnalyzerFieldConfig {
  keys: string[];
  nestedKeys?: string[];
  joinWith?: string;
}

export interface CaseAnalyzerSuggestionPayload {
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
  abstract?: string;
  notes?: string;
  raw_data?: string | Record<string, unknown>;
}

export interface SuggestionResponse {
  id: number;
  status?: string;
}

export interface CaseAnalyzerSuggestionRecord {
  id: number;
  payload?: Record<string, unknown> | null;
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
  status: "pending" | "in_progress" | "completed" | "error";
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
    keys: ["case_citation_edited", "case_citation"],
    nestedKeys: ["case_citation"],
  },
  jurisdiction: {
    keys: ["jurisdiction_edited", "jurisdiction"],
    nestedKeys: ["precise_jurisdiction"],
  },
  caseAbstract: {
    keys: ["abstract_edited", "abstract"],
    nestedKeys: ["abstract"],
  },
  caseRelevantFacts: {
    keys: ["relevant_facts_edited", "relevant_facts"],
    nestedKeys: ["relevant_facts"],
  },
  casePILProvisions: {
    keys: ["legal_provisions_edited", "legal_provisions", "pil_provisions"],
    nestedKeys: ["legal_provisions", "pil_provisions"],
    joinWith: ", ",
  },
  caseChoiceofLawIssue: {
    keys: ["choice_of_law_issue_edited", "choice_of_law_issue"],
    nestedKeys: ["choice_of_law_issue"],
  },
  caseCourtsPosition: {
    keys: ["courts_position_edited", "courts_position"],
    nestedKeys: ["courts_position"],
  },
  caseObiterDicta: {
    keys: ["obiter_dicta_edited", "obiter_dicta"],
    nestedKeys: ["obiter_dicta"],
  },
  caseDissentingOpinions: {
    keys: ["dissenting_opinions_edited", "dissenting_opinions"],
    nestedKeys: ["dissenting_opinions"],
  },
};

export const ANALYSIS_STEP_KEYS = [
  "col_extraction",
  "theme_classification",
  "case_citation",
  "abstract",
  "relevant_facts",
  "pil_provisions",
  "col_issue",
  "courts_position",
  "obiter_dicta",
  "dissenting_opinions",
] as const;
