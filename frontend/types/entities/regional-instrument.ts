/**
 * Regional Instrument entity type definitions
 */

/** Raw API response */
export interface RegionalInstrumentResponse {
  id: string;
  source_table?: string;
  rank?: number;
  ID?: string;
  "ID Number"?: string;
  Title?: string;
  Abbreviation?: string;
  Date?: string;
  URL?: string;
  Attachment?: string;
  "Record ID"?: string;
  Created?: string;
  "Last Modified"?: string;
  sort_date?: string;
  // Nested mappings
  Specialists?: string;
  "Specialists Link"?: string;
  "Regional Legal Provisions"?: string;
  "Regional Legal Provisions Link"?: string;
  // Legacy fields
  "Title (in English)"?: string;
  Name?: string;
  Literature?: string;
  "OUP Chapter"?: string;
  Link?: string;
}

/** Processed type with normalized fields */
export interface RegionalInstrument extends RegionalInstrumentResponse {
  "Title (in English)": string;
  URL: string;
}

/** Transform raw response to processed type */
export function processRegionalInstrument(
  raw: RegionalInstrumentResponse,
): RegionalInstrument {
  return {
    ...raw,
    "Title (in English)": raw["Title (in English)"] || raw.Name || "",
    "Last Modified": formatDate(raw["Last Modified"] || raw.Created),
    Date: formatDate(raw.Date),
    URL: raw.URL || raw.Link || "",
  };
}
