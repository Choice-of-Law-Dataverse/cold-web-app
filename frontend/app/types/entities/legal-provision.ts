import { formatDate } from "@/utils/format";

interface BaseLegalProvisionResponse {
  id: string;
  sourceTable?: string;
  rank?: number;
  ID?: string;
  recordId?: string;
  Created?: string;
  lastModified?: string;
}

export interface DomesticLegalProvisionResponse extends BaseLegalProvisionResponse {
  Name?: string;
  Article?: string;
  fullTextOfTheProvisionOriginalLanguage?: string;
  fullTextOfTheProvisionEnglishTranslation?: string;
  rankingDisplayOrder?: string;
  domesticInstrumentsLink?: string;
  legislationTitle?: string;
  Answers?: string;
  Questions?: string;
  themesLink?: string;
  jurisdictionsLink?: string;
  Jurisdictions?: string;
}

export interface RegionalLegalProvisionResponse extends BaseLegalProvisionResponse {
  titleOfTheProvision?: string;
  fullText?: string;
  Provision?: string;
  sortDate?: string;
  Instrument?: string;
  instrumentLink?: string;
  Questions?: string;
}

export interface InternationalLegalProvisionResponse extends BaseLegalProvisionResponse {
  titleOfTheProvision?: string;
  fullText?: string;
  Provision?: string;
  sortDate?: string;
  Instrument?: string;
  rankingDisplayOrder?: string;
  instrumentLink?: string;
}

export interface LegalProvision {
  id: string;
  title: string;
  originalText: string;
  englishText?: string;
  hasEnglishTranslation: boolean;
  lastModified?: string;
}

export function processDomesticLegalProvision(
  raw: DomesticLegalProvisionResponse,
): LegalProvision {
  const englishText = raw.fullTextOfTheProvisionEnglishTranslation;
  return {
    id: raw.id,
    title: raw.Article || "Unknown Article",
    originalText:
      raw.fullTextOfTheProvisionOriginalLanguage || "No content available",
    englishText: englishText || undefined,
    hasEnglishTranslation: Boolean(englishText),
    lastModified: formatDate(raw.lastModified || raw.Created),
  };
}

export function processRegionalLegalProvision(
  raw: RegionalLegalProvisionResponse,
): LegalProvision {
  return {
    id: raw.id,
    title: raw.titleOfTheProvision || "Unknown Article",
    originalText: raw.fullText || "No content available",
    englishText: undefined,
    hasEnglishTranslation: false,
    lastModified: formatDate(raw.lastModified || raw.Created),
  };
}
