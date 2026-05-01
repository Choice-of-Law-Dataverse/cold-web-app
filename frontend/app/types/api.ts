import type { components } from "./api-schema";
import type { AnySearchResult as AnySearchResultType } from "./search";
import type { AnswerResponse, AnswerDetailResponse } from "./entities/answer";
import type {
  ArbitralAwardResponse,
  ArbitralAwardDetailResponse,
} from "./entities/arbitral-award";
import type {
  ArbitralInstitutionResponse,
  ArbitralInstitutionDetailResponse,
} from "./entities/arbitral-institution";
import type {
  ArbitralRuleResponse,
  ArbitralRuleDetailResponse,
} from "./entities/arbitral-rule";
import type {
  CourtDecisionResponse,
  CourtDecisionDetailResponse,
} from "./entities/court-decision";
import type {
  DomesticInstrumentResponse,
  DomesticInstrumentDetailResponse,
} from "./entities/domestic-instrument";
import type {
  InternationalInstrumentResponse,
  InternationalInstrumentDetailResponse,
} from "./entities/international-instrument";
import type {
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
  LiteratureResponse,
  LiteratureDetailResponse,
} from "./entities/literature";
import type { QuestionResponse } from "./entities/question";
import type {
  RegionalInstrumentResponse,
  RegionalInstrumentDetailResponse,
} from "./entities/regional-instrument";
import type {
  SpecialistResponse,
  SpecialistDetailResponse,
} from "./entities/specialist";
import type { HcchAnswerDetailResponse } from "./entities/hcch-answer";

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

export type TypedFilter<T extends TableName> = {
  column: keyof TableResponseMap[T] & string;
  value: string | number | boolean;
};

export type { AnySearchResult } from "./search";

export interface SearchResponse {
  results: AnySearchResultType[];
  totalMatches: number;
}

export type JurisdictionWithAnswerCoverage =
  components["schemas"]["JurisdictionCoverage"];

export interface JurisdictionCount {
  jurisdiction: string;
  n: number;
}
