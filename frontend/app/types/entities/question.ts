/**
 * Question entity type definitions
 */

import { formatDate } from "@/utils/format";

/** Raw API response */
export interface QuestionResponse {
  id: string;
  sourceTable?: string;
  rank?: number;
  ID?: string;
  question?: string;
  questionNumber?: string;
  Created?: string;
  recordId?: string;
  themeCode?: string;
  answeringOptions?: string;
  lastModified?: string;
  sortDate?: string;
  themes?: string;
  answer?: string;
  moreInformation?: string;
  domesticLegalProvisions?: string;
  domesticLegalProvisionsLink?: string;
  domesticInstruments?: string;
  domesticInstrumentsId?: string;
  domesticInstrumentsLink?: string;
  oupChapter?: string;
  oupBookQuote?: string;
  courtDecisionsId?: string;
  relatedLiterature?: string;
  countryReport?: string;
  jurisdictions?: string;
  jurisdictionsAlpha3Code?: string;
  jurisdictionsLiteratureId?: string;
  jurisdictionsLink?: string;
  jurisdictionsRegion?: string;
}

/** Processed type with normalized fields */
export interface Question extends Omit<QuestionResponse, "courtDecisionsId"> {
  domesticLegalProvisions: string;
  courtDecisionsId: string[];
  JurisdictionCode: string;
}

export function processQuestion(raw: QuestionResponse): Question {
  const courtDecisionsId = raw.courtDecisionsId;

  return {
    ...raw,
    lastModified: formatDate(raw.lastModified || raw.Created),
    domesticLegalProvisions: raw.domesticLegalProvisions || "",
    courtDecisionsId:
      typeof courtDecisionsId === "string"
        ? courtDecisionsId.split(",").map((caseId) => caseId.trim())
        : [],
    JurisdictionCode: raw.jurisdictionsAlpha3Code || "",
  };
}
