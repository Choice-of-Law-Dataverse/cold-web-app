/**
 * Domestic Instrument entity type definitions
 */

export interface DomesticInstrumentResponse {
  id: string;
  "Title (in English)"?: string;
  "Official Title"?: string;
  Abbreviation?: string;
  Date?: string;
  "Entry Into Force"?: string;
  "Publication Date"?: string;
  Compatibility?: boolean;
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
