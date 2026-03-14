import type { components } from "./api-schema";
import type { AnswerResponse, AnswerDetailResponse } from "./entities/answer";
import type {
  ArbitralAward,
  ArbitralAwardResponse,
  ArbitralAwardDetailResponse,
} from "./entities/arbitral-award";
import type {
  ArbitralInstitution,
  ArbitralInstitutionResponse,
  ArbitralInstitutionDetailResponse,
} from "./entities/arbitral-institution";
import type {
  ArbitralRule,
  ArbitralRuleResponse,
  ArbitralRuleDetailResponse,
} from "./entities/arbitral-rule";
import type {
  CourtDecision,
  CourtDecisionResponse,
  CourtDecisionDetailResponse,
} from "./entities/court-decision";
import type {
  DomesticInstrument,
  DomesticInstrumentResponse,
  DomesticInstrumentDetailResponse,
} from "./entities/domestic-instrument";
import type {
  InternationalInstrument,
  InternationalInstrumentResponse,
  InternationalInstrumentDetailResponse,
} from "./entities/international-instrument";
import type {
  Jurisdiction,
  JurisdictionResponse,
  JurisdictionDetailResponse,
} from "./entities/jurisdiction";
import type {
  DomesticLegalProvisionResponse,
  DomesticLegalProvisionDetailResponse,
  InternationalLegalProvisionResponse,
  InternationalLegalProvisionDetailResponse,
  RegionalLegalProvisionResponse,
  RegionalLegalProvisionDetailResponse,
} from "./entities/legal-provision";
import type {
  Literature,
  LiteratureResponse,
  LiteratureDetailResponse,
} from "./entities/literature";
import type { Question, QuestionResponse } from "./entities/question";
import type {
  RegionalInstrument,
  RegionalInstrumentResponse,
  RegionalInstrumentDetailResponse,
} from "./entities/regional-instrument";
import type {
  Specialist,
  SpecialistResponse,
  SpecialistDetailResponse,
} from "./entities/specialist";
import type {
  HcchAnswer,
  HcchAnswerDetailResponse,
} from "./entities/hcch-answer";

export { ApiError } from "./errors";

export interface SearchFilters {
  jurisdiction?: string;
  theme?: string;
  type?: string;
  sortBy?: "date" | "relevance";
}

export interface FilterObjectOption {
  label: string;
  coldId?: string;
}

export type FilterOption = FilterObjectOption | string;

export interface SearchParams {
  query: string;
  filters: SearchFilters;
  page?: number;
  pageSize?: number;
  enabledOverride?: boolean;
}

export type TableName =
  | "Answers"
  | "Arbitral Awards"
  | "Arbitral Institutions"
  | "Arbitral Rules"
  | "Court Decisions"
  | "Domestic Instruments"
  | "HCCH Answers"
  | "Domestic Legal Provisions"
  | "International Instruments"
  | "International Legal Provisions"
  | "Jurisdictions"
  | "Leading Cases"
  | "Literature"
  | "Questions"
  | "Regional Instruments"
  | "Regional Legal Provisions"
  | "Specialists";

export type TableResponseMap = {
  Answers: AnswerResponse;
  "Arbitral Awards": ArbitralAwardResponse;
  "Arbitral Institutions": ArbitralInstitutionResponse;
  "Arbitral Rules": ArbitralRuleResponse;
  "Court Decisions": CourtDecisionResponse;
  "Domestic Instruments": DomesticInstrumentResponse;
  "Domestic Legal Provisions": DomesticLegalProvisionResponse;
  "HCCH Answers": HcchAnswerDetailResponse;
  "International Instruments": InternationalInstrumentResponse;
  "International Legal Provisions": InternationalLegalProvisionResponse;
  Jurisdictions: JurisdictionResponse;
  "Leading Cases": CourtDecisionResponse;
  Literature: LiteratureResponse;
  Questions: QuestionResponse;
  "Regional Instruments": RegionalInstrumentResponse;
  "Regional Legal Provisions": RegionalLegalProvisionResponse;
  Specialists: SpecialistResponse;
};

export type TableDetailMap = {
  Answers: AnswerDetailResponse;
  "Arbitral Awards": ArbitralAwardDetailResponse;
  "Arbitral Institutions": ArbitralInstitutionDetailResponse;
  "Arbitral Rules": ArbitralRuleDetailResponse;
  "Court Decisions": CourtDecisionDetailResponse;
  "Domestic Instruments": DomesticInstrumentDetailResponse;
  "Domestic Legal Provisions": DomesticLegalProvisionDetailResponse;
  "HCCH Answers": HcchAnswerDetailResponse;
  "International Instruments": InternationalInstrumentDetailResponse;
  "International Legal Provisions": InternationalLegalProvisionDetailResponse;
  Jurisdictions: JurisdictionDetailResponse;
  "Leading Cases": CourtDecisionDetailResponse;
  Literature: LiteratureDetailResponse;
  Questions: AnswerDetailResponse;
  "Regional Instruments": RegionalInstrumentDetailResponse;
  "Regional Legal Provisions": RegionalLegalProvisionDetailResponse;
  Specialists: SpecialistDetailResponse;
};

export type TableProcessedMap = {
  Answers: AnswerDetailResponse;
  "Arbitral Awards": ArbitralAward;
  "Arbitral Institutions": ArbitralInstitution;
  "Arbitral Rules": ArbitralRule;
  "Court Decisions": CourtDecision;
  "Domestic Instruments": DomesticInstrument;
  "Domestic Legal Provisions": DomesticLegalProvisionDetailResponse;
  "HCCH Answers": HcchAnswer;
  "International Instruments": InternationalInstrument;
  "International Legal Provisions": InternationalLegalProvisionDetailResponse;
  Jurisdictions: Jurisdiction;
  "Leading Cases": CourtDecision;
  Literature: Literature;
  Questions: Question;
  "Regional Instruments": RegionalInstrument;
  "Regional Legal Provisions": RegionalLegalProvisionDetailResponse;
  Specialists: Specialist;
};

export type TypedFilter<T extends TableName> = {
  column: keyof TableResponseMap[T] & string;
  value: string | number | boolean;
};

export type FilterColumn = "jurisdictions" | "themes" | "tables" | "type";

export interface SearchResponse {
  results: Record<string, unknown>[];
  totalMatches: number;
}

export type JurisdictionWithAnswerCoverage =
  components["schemas"]["JurisdictionCoverage"];

export interface JurisdictionCount {
  jurisdiction: string;
  n: number;
}
