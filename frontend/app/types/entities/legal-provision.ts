import type { components } from "@/types/api-schema";

export type DomesticLegalProvisionResponse =
  components["schemas"]["DomesticLegalProvisionRecord"];
export type DomesticLegalProvisionDetailResponse =
  components["schemas"]["DomesticLegalProvisionDetail"];
export type RegionalLegalProvisionResponse =
  components["schemas"]["RegionalLegalProvisionRecord"];
export type RegionalLegalProvisionDetailResponse =
  components["schemas"]["RegionalLegalProvisionDetail"];
export type InternationalLegalProvisionResponse =
  components["schemas"]["InternationalLegalProvisionRecord"];
export type InternationalLegalProvisionDetailResponse =
  components["schemas"]["InternationalLegalProvisionDetail"];

export interface LegalProvision {
  id: string | number | null | undefined;
  title: string;
  originalText: string;
  englishText?: string;
  hasEnglishTranslation: boolean;
}

export function processDomesticLegalProvision(
  raw: DomesticLegalProvisionDetailResponse,
): LegalProvision {
  const englishText = raw.fullTextOfTheProvisionEnglishTranslation;
  return {
    id: raw.id,
    title: raw.article || "Unknown Article",
    originalText:
      raw.fullTextOfTheProvisionOriginalLanguage || "No content available",
    englishText: englishText || undefined,
    hasEnglishTranslation: Boolean(englishText),
  };
}

export function processRegionalLegalProvision(
  raw: RegionalLegalProvisionDetailResponse,
): LegalProvision {
  return {
    id: raw.id,
    title: raw.titleOfTheProvision || "Unknown Article",
    originalText: raw.fullText || "No content available",
    englishText: undefined,
    hasEnglishTranslation: false,
  };
}

export function processInternationalLegalProvision(
  raw: InternationalLegalProvisionDetailResponse,
): LegalProvision {
  return {
    id: raw.id,
    title: raw.titleOfTheProvision || "Unknown Article",
    originalText: raw.fullText || "No content available",
    englishText: undefined,
    hasEnglishTranslation: false,
  };
}
