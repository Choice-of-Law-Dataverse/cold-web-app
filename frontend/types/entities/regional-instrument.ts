/**
 * Regional Instrument entity type definitions
 */

/** Raw API response */
export interface RegionalInstrumentResponse {
  id: string;
  Abbreviation?: string;
  Title?: string;
  "Title (in English)"?: string;
  Name?: string;
  Date?: string;
  Specialists?: string;
  Literature?: string;
  "OUP Chapter"?: string;
  "Regional Legal Provisions"?: string;
  URL?: string;
  Link?: string;
  Attachment?: string;
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
    URL: raw.URL || raw.Link || "",
  };
}
