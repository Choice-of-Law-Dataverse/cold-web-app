/**
 * Domestic Instrument entity type definitions
 */

/** Raw API response */
export interface DomesticInstrumentResponse {
  id: string;
  "Title (in English)"?: string;
  "Official Title"?: string;
  Abbreviation?: string;
  Date?: string;
  "Entry Into Force"?: string;
  "Publication Date"?: string;
  "Compatible With the UNCITRAL Model Law"?: boolean | string;
  "Compatible With the HCCH Principles"?: boolean | string;
  "Amended by"?: string;
  Amends?: string;
  Replaces?: string;
  "Replaced by"?: string;
  "Domestic Legal Provisions"?: string;
  "OUP Chapter"?: string;
  "Country Report"?: string;
  "Ranking (Display Order)"?: string;
  "Jurisdictions Alpha-3 Code"?: string;
  "Official Source (PDF)"?: string;
  "Source (PDF)"?: string;
  "Source (URL)"?: string;
}

/** Processed type with normalized fields */
export interface DomesticInstrument extends DomesticInstrumentResponse {
  "Title (in English)": string;
  Compatibility?: boolean;
}

/** Transform raw response to processed type */
export function processDomesticInstrument(
  raw: DomesticInstrumentResponse,
): DomesticInstrument {
  const hasCompatibility =
    raw["Compatible With the UNCITRAL Model Law"] === true ||
    raw["Compatible With the HCCH Principles"] === true;

  return {
    ...raw,
    "Title (in English)": raw["Title (in English)"] || raw["Official Title"] || "",
    Compatibility: hasCompatibility ? true : undefined,
  };
}
