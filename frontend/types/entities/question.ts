/**
 * Question entity type definitions
 */

/** Raw API response */
export interface QuestionResponse {
  id: string;
  source_table?: string;
  rank?: number;
  ID?: string;
  Question?: string;
  Question_Number?: string;
  Created?: string;
  "Record ID"?: string;
  Theme_Code?: string;
  Answering_Options?: string;
  "Last Modified"?: string;
  sort_date?: string;
  // Nested mappings
  Themes?: string;
  // Legacy fields for backwards compatibility
  Answer?: string;
  "More Information"?: string;
  "Domestic Legal Provisions"?: string;
  "OUP Chapter"?: string;
  "OUP Book Quote"?: string;
  "Court Decisions ID"?: string;
  "Related Literature"?: string;
  "Country Report"?: string;
  Jurisdictions?: string;
  "Jurisdictions Alpha-3 code"?: string;
  "Jurisdictions Alpha-3 Code"?: string;
  "Jurisdictions Literature ID"?: string;
}

/** Processed type with normalized fields */
export interface Question extends Omit<QuestionResponse, "Court Decisions ID"> {
  "Domestic Legal Provisions": string;
  "Court Decisions ID": string[];
}

/** Transform raw response to processed type */
export function processQuestion(raw: QuestionResponse): Question {
  const courtDecisionsId = raw["Court Decisions ID"];

  return {
    ...raw,
    "Domestic Legal Provisions": raw["Domestic Legal Provisions"] || "",
    "Court Decisions ID":
      typeof courtDecisionsId === "string"
        ? courtDecisionsId.split(",").map((caseId) => caseId.trim())
        : [],
  };
}
