/**
 * International Instrument entity type definitions
 */

/** Raw API response */
export interface InternationalInstrumentResponse {
  id: string;
  Name?: string;
  Date?: string;
  Specialists?: string;
  Literature?: string;
  "OUP Chapter"?: string;
  "Selected Provisions"?: string;
  URL?: string;
  Link?: string;
  Attachment?: string;
  Abbreviation?: string;
  "Title (in English)"?: string;
}

/** Processed type with normalized fields */
export interface InternationalInstrument extends InternationalInstrumentResponse {
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
