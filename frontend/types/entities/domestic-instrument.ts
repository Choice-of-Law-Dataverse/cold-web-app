/**
 * Domestic Instrument entity type definitions
 */

import { formatDate } from "@/utils/format";

/** Raw API response */
export interface DomesticInstrumentResponse {
  id: string;
  source_table?: string;
  rank?: number;
  ID?: string;
  "ID-number"?: string;
  Date?: string;
  Status?: string;
  Abbreviation?: string;
  "Relevant Provisions"?: string;
  "Record ID"?: string;
  Created?: string;
  "Last Modified"?: string;
  "Entry Into Force"?: string;
  "Publication Date"?: string;
  "Full Text of the Provisions"?: string;
  "Official Title"?: string;
  sort_date?: string;
  "Title (in English)"?: string;
  "Source (URL)"?: string;
  "Source (PDF)"?: string;
  "Compatible With the HCCH Principles"?: boolean | string;
  "Compatible With the UNCITRAL Model Law"?: boolean | string;
  // Nested mappings
  "Jurisdictions Link"?: string;
  "Jurisdictions Alpha-3 Code"?: string;
  Jurisdictions?: string;
  "Type (from Jurisdictions)"?: string;
  "Question ID"?: string;
  "Answers Link"?: string;
  "Domestic Legal Provisions Link"?: string;
  "Domestic Legal Provisions Full Text of the Provision (English T"?: string;
  "Domestic Legal Provisions Full Text of the Provision (Original "?: string;
  "Domestic Legal Provisions"?: string;
  // Legacy fields
  "Amended by"?: string;
  Amends?: string;
  Replaces?: string;
  "Replaced by"?: string;
  "OUP Chapter"?: string;
  "Country Report"?: string;
  "Ranking (Display Order)"?: string;
  "Official Source (PDF)"?: string;
}

/** Processed type with normalized fields */
export interface DomesticInstrument extends DomesticInstrumentResponse {
  "Title (in English)": string;
  Compatibility?: boolean;
  /** Pre-computed display title with fallback: Abbreviation → Title (in English) → Official Title → id */
  displayTitle: string;
}

/** Transform raw response to processed type */
export function processDomesticInstrument(
  raw: DomesticInstrumentResponse,
): DomesticInstrument {
  const hasCompatibility =
    raw["Compatible With the UNCITRAL Model Law"] === true ||
    raw["Compatible With the HCCH Principles"] === true;

  const titleInEnglish =
    raw["Title (in English)"] || raw["Official Title"] || "";
  const displayTitle =
    raw.Abbreviation || titleInEnglish || raw["Official Title"] || raw.id;

  return {
    ...raw,
    Date: formatDate(raw.Date),
    "Publication Date": formatDate(raw["Publication Date"]),
    "Last Modified": formatDate(raw["Last Modified"] || raw.Created),
    "Title (in English)": titleInEnglish,
    Compatibility: hasCompatibility ? true : undefined,
    displayTitle,
  };
}
