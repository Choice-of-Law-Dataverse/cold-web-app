/**
 * Question (Answer) entity type definitions
 */

/** Raw API response */
export interface QuestionResponse {
  id: string;
  Question?: string;
  Answer?: string;
  "More Information"?: string;
  "Domestic Legal Provisions"?: string;
  "OUP Chapter"?: string;
  "OUP Book Quote"?: string;
  "Court Decisions ID"?: string;
  "Related Literature"?: string;
  "Country Report"?: string;
  "Last Modified"?: string;
  Created?: string;
  Jurisdictions?: string;
  "Jurisdictions Alpha-3 code"?: string;
  "Jurisdictions Alpha-3 Code"?: string;
  "Jurisdictions Literature ID"?: string;
  Themes?: string;
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
