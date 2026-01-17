/**
 * International Instrument entity type definitions
 */

/** Raw API response */
export interface InternationalInstrumentResponse {
  id: string;
  source_table?: string;
  rank?: number;
  ID?: string;
  "ID Number"?: string;
  Title?: string;
  Abbreviation?: string;
  Date?: string;
  Status?: string;
  URL?: string;
  Attachment?: string;
  "Record ID"?: string;
  Created?: string;
  "Last Modified"?: string;
  "Entry Into Force"?: string;
  "Publication Date"?: string;
  "Relevant Provisions"?: string;
  "Full Text of the Provisions"?: string;
  Name?: string;
  sort_date?: string;
  "Title (in English)"?: string;
  "Source (URL)"?: string;
  "Source (PDF)"?: string;
  // Nested mappings
  Specialists?: string;
  "Specialists Link"?: string;
  "International Legal Provisions"?: string;
  "International Legal Provisions Link"?: string;
  Literature?: string;
  "Literature Link"?: string;
  "HCCH Answers"?: string;
  "HCCH Answers Link"?: string;
  // Legacy fields
  Link?: string;
  "OUP Chapter"?: string;
  "Selected Provisions"?: string;
}

/** Processed type with normalized fields */
export interface InternationalInstrument
  extends InternationalInstrumentResponse {
  "Title (in English)": string;
  URL: string;
}

/** Transform raw response to processed type */
export function processInternationalInstrument(
  raw: InternationalInstrumentResponse,
): InternationalInstrument {
  return {
    ...raw,
    "Title (in English)": raw["Title (in English)"] || raw.Name || "",
    URL: raw.URL || raw.Link || "",
  };
}
