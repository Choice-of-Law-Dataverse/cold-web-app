import type { components } from "@/types/api-schema";
import { formatDate } from "@/utils/format";

export type DomesticLegalProvisionResponse =
  components["schemas"]["DomesticLegalProvisionRecord"];
export type RegionalLegalProvisionResponse =
  components["schemas"]["RegionalLegalProvisionRecord"];
export type InternationalLegalProvisionResponse =
  components["schemas"]["InternationalLegalProvisionRecord"];

export interface LegalProvision {
  id: string | number | null | undefined;
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
    title: raw.article || "Unknown Article",
    originalText:
      raw.fullTextOfTheProvisionOriginalLanguage || "No content available",
    englishText: englishText || undefined,
    hasEnglishTranslation: Boolean(englishText),
    lastModified: formatDate(raw.lastModified || raw.created),
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
    lastModified: formatDate(raw.lastModified || raw.created),
  };
}
