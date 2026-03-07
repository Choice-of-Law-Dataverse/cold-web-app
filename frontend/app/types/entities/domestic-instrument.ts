/**
 * Domestic Instrument entity type definitions
 */

import { formatDate } from "@/utils/format";

/** Raw API response */
export interface DomesticInstrumentResponse {
  id: string;
  sourceTable?: string;
  rank?: number;
  ID?: string;
  idNumber?: string;
  Date?: string;
  Status?: string;
  Abbreviation?: string;
  relevantProvisions?: string;
  recordId?: string;
  Created?: string;
  lastModified?: string;
  entryIntoForce?: string;
  publicationDate?: string;
  fullTextOfTheProvisions?: string;
  officialTitle?: string;
  sortDate?: string;
  titleInEnglish?: string;
  sourceUrl?: string;
  sourcePdf?: string;
  compatibleWithTheHcchPrinciples?: boolean | string;
  compatibleWithTheUncitralModelLaw?: boolean | string;
  jurisdictionsLink?: string;
  jurisdictionsAlpha3Code?: string;
  jurisdictions?: string;
  typeFromJurisdictions?: string;
  questionId?: string;
  answersLink?: string;
  domesticLegalProvisionsLink?: string;
  domesticLegalProvisionsFullTextOfTheProvisionEnglishT?: string;
  domesticLegalProvisionsFullTextOfTheProvisionOriginal?: string;
  domesticLegalProvisions?: string;
  amendedBy?: string;
  Amends?: string;
  Replaces?: string;
  replacedBy?: string;
  oupChapter?: string;
  countryReport?: string;
  rankingDisplayOrder?: string;
  officialSourcePdf?: string;
}

/** Processed type with normalized fields */
export interface DomesticInstrument extends DomesticInstrumentResponse {
  titleInEnglish: string;
  Compatibility?: boolean;
  displayTitle: string;
}

export function processDomesticInstrument(
  raw: DomesticInstrumentResponse,
): DomesticInstrument {
  const hasCompatibility =
    raw.compatibleWithTheUncitralModelLaw === true ||
    raw.compatibleWithTheHcchPrinciples === true;

  const titleInEnglish = raw.titleInEnglish || raw.officialTitle || "";
  const displayTitle =
    raw.Abbreviation || titleInEnglish || raw.officialTitle || raw.id;

  return {
    ...raw,
    Date: formatDate(raw.Date),
    publicationDate: formatDate(raw.publicationDate),
    lastModified: formatDate(raw.lastModified || raw.Created),
    titleInEnglish,
    Compatibility: hasCompatibility ? true : undefined,
    displayTitle,
  };
}
