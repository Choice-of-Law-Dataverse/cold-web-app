/**
 * Legal Provision entity type definitions
 */

import { formatDate } from "@/utils/format";

/** Base fields shared by all legal provisions */
interface BaseLegalProvisionResponse {
  id: string;
  source_table?: string;
  rank?: number;
  ID?: string;
  "Record ID"?: string;
  Created?: string;
  "Last Modified"?: string;
}

/** Domestic Legal Provisions API response */
export interface DomesticLegalProvisionResponse extends BaseLegalProvisionResponse {
  Name?: string;
  Article?: string;
  "Full Text of the Provision (Original Language)"?: string;
  "Full Text of the Provision (English Translation)"?: string;
  "Ranking (Display Order)"?: string;
  // Nested mappings
  "Domestic Instruments Link"?: string;
  "Legislation Title"?: string;
  Answers?: string;
  Questions?: string;
  "Themes Link"?: string;
  "Jurisdictions Link"?: string;
  Jurisdictions?: string;
}

/** Regional Legal Provisions API response */
export interface RegionalLegalProvisionResponse extends BaseLegalProvisionResponse {
  "Title of the Provision"?: string;
  "Full Text"?: string;
  Provision?: string;
  sort_date?: string;
  Instrument?: string;
  // Nested mappings
  "Instrument Link"?: string;
  Questions?: string;
}

/** International Legal Provisions API response */
export interface InternationalLegalProvisionResponse extends BaseLegalProvisionResponse {
  "Title of the Provision"?: string;
  "Full Text"?: string;
  Provision?: string;
  sort_date?: string;
  Instrument?: string;
  Ranking__Display_Order_?: string;
  // Nested mappings
  "Instrument Link"?: string;
}

/** Processed Legal Provision with normalized fields */
export interface LegalProvision {
  id: string;
  title: string;
  originalText: string;
  englishText?: string;
  hasEnglishTranslation: boolean;
  "Last Modified"?: string;
}

/** Process domestic legal provision */
export function processDomesticLegalProvision(
  raw: DomesticLegalProvisionResponse,
): LegalProvision {
  const englishText = raw["Full Text of the Provision (English Translation)"];
  return {
    id: raw.id,
    title: raw.Article || "Unknown Article",
    originalText:
      raw["Full Text of the Provision (Original Language)"] ||
      "No content available",
    englishText: englishText || undefined,
    hasEnglishTranslation: Boolean(englishText),
    "Last Modified": formatDate(raw["Last Modified"] || raw.Created),
  };
}

/** Process regional legal provision */
export function processRegionalLegalProvision(
  raw: RegionalLegalProvisionResponse,
): LegalProvision {
  return {
    id: raw.id,
    title: raw["Title of the Provision"] || "Unknown Article",
    originalText: raw["Full Text"] || "No content available",
    englishText: undefined,
    hasEnglishTranslation: false,
    "Last Modified": formatDate(raw["Last Modified"] || raw.Created),
  };
}
