import type { components } from "./api-schema";

export type SearchResultBase = components["schemas"]["SearchResultBase"];
export type AnswerSearchResult = components["schemas"]["AnswerSearchResult"];
export type CourtDecisionSearchResult =
  components["schemas"]["CourtDecisionSearchResult"];
export type DomesticInstrumentSearchResult =
  components["schemas"]["DomesticInstrumentSearchResult"];
export type RegionalInstrumentSearchResult =
  components["schemas"]["RegionalInstrumentSearchResult"];
export type InternationalInstrumentSearchResult =
  components["schemas"]["InternationalInstrumentSearchResult"];
export type LiteratureSearchResult =
  components["schemas"]["LiteratureSearchResult"];
export type ArbitralAwardSearchResult =
  components["schemas"]["ArbitralAwardSearchResult"];
export type ArbitralRuleSearchResult =
  components["schemas"]["ArbitralRuleSearchResult"];
export type ArbitralInstitutionSearchResult =
  components["schemas"]["ArbitralInstitutionSearchResult"];
export type ArbitralProvisionSearchResult =
  components["schemas"]["ArbitralProvisionSearchResult"];
export type DomesticLegalProvisionSearchResult =
  components["schemas"]["DomesticLegalProvisionSearchResult"];
export type InternationalLegalProvisionSearchResult =
  components["schemas"]["InternationalLegalProvisionSearchResult"];
export type RegionalLegalProvisionSearchResult =
  components["schemas"]["RegionalLegalProvisionSearchResult"];
export type JurisdictionSearchResult =
  components["schemas"]["JurisdictionSearchResult"];
export type QuestionSearchResult =
  components["schemas"]["QuestionSearchResult"];

export type AnySearchResult =
  | AnswerSearchResult
  | CourtDecisionSearchResult
  | DomesticInstrumentSearchResult
  | RegionalInstrumentSearchResult
  | InternationalInstrumentSearchResult
  | LiteratureSearchResult
  | ArbitralAwardSearchResult
  | ArbitralRuleSearchResult
  | ArbitralInstitutionSearchResult
  | ArbitralProvisionSearchResult
  | DomesticLegalProvisionSearchResult
  | InternationalLegalProvisionSearchResult
  | RegionalLegalProvisionSearchResult
  | JurisdictionSearchResult
  | QuestionSearchResult
  | SearchResultBase;

type KeysOf<T> = T extends unknown ? keyof T : never;
export type AnySearchResultKey = KeysOf<AnySearchResult> & string;

export function searchResultField(
  data: AnySearchResult,
  key: AnySearchResultKey,
): unknown {
  return data[key as keyof typeof data];
}
