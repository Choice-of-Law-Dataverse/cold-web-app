/**
 * Answer entity type definitions
 */

/** Raw API response */
export interface AnswerResponse {
  id: string;
  source_table?: string;
  rank?: number;
  ID?: string;
  "CoLD ID"?: string;
  "Question ID"?: string;
  "Answer ID"?: string;
  Answer?: string;
  "Record ID"?: string;
  Created?: string;
  "Last Modified"?: string;
  "To Review?"?: boolean;
  "OUP Book Quote"?: string;
  "More Information"?: string;
  sort_date?: string;
  // Nested mappings from related questions
  "Question Link"?: string;
  Question?: string;
  Number?: string;
  "Questions Theme Code"?: string;
  // Nested mappings from related jurisdictions
  "Jurisdictions Link"?: string;
  "Jurisdictions Alpha-3 Code"?: string;
  "Jurisdictions Alpha-3 code"?: string; // backwards compat
  Jurisdictions?: string;
  "Jurisdictions Region"?: string;
  "Jurisdictions Irrelevant"?: boolean | string;
  // Nested mappings from hop1 relations
  "Court Decisions"?: string;
  "Court Decisions Link"?: string;
  "Court Decisions ID"?: string;
  "Domestic Instruments Link"?: string;
  "Domestic Instruments"?: string;
  "Domestic Instruments ID"?: string;
  "Domestic Legal Provisions Link"?: string;
  "Domestic Legal Provisions"?: string;
  Themes?: string;
}
