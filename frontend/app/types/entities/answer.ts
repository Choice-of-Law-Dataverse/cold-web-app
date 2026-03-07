/**
 * Answer entity type definitions
 */

/** Raw API response */
export interface AnswerResponse {
  id: string;
  sourceTable?: string;
  rank?: number;
  ID?: string;
  coldId?: string;
  questionId?: string;
  answerId?: string;
  answer?: string;
  recordId?: string;
  Created?: string;
  lastModified?: string;
  toReview?: boolean;
  oupBookQuote?: string;
  moreInformation?: string;
  sortDate?: string;
  questionLink?: string;
  question?: string;
  number?: string;
  questionsThemeCode?: string;
  jurisdictionsLink?: string;
  jurisdictionsAlpha3Code?: string;
  jurisdictions?: string;
  jurisdictionsRegion?: string;
  jurisdictionsIrrelevant?: boolean | string;
  courtDecisions?: string;
  courtDecisionsLink?: string;
  courtDecisionsId?: string;
  domesticInstrumentsLink?: string;
  domesticInstruments?: string;
  domesticInstrumentsId?: string;
  domesticLegalProvisionsLink?: string;
  domesticLegalProvisions?: string;
  themes?: string;
}
