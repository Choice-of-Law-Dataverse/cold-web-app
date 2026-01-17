/**
 * Court Decision entity type definitions
 */

import { formatDate } from "@/utils/format";

/** Raw API response */
export interface CourtDecisionResponse {
  id: string;
  source_table?: string;
  rank?: number;
  ID?: string;
  "Case Citation"?: string;
  "Case Title"?: string;
  Instance?: string;
  Date?: string;
  Abstract?: string;
  Created?: string;
  "Record ID"?: string;
  "ID-number"?: string;
  "Last Modified"?: string;
  "Answers Link"?: string;
  "Answers Question"?: string;
  Text_of_the_Relevant_Legal_Provisions?: string;
  Quote?: string;
  "Case Rank"?: string;
  "English Translation"?: string;
  "Choice of Law Issue"?: string;
  "Court's Position"?: string;
  "Translated Excerpt"?: string;
  "Relevant Facts"?: string;
  "Date of Judgment"?: string;
  "PIL Provisions"?: string;
  "Original Text"?: string;
  sort_date?: string;
  "Publication Date ISO"?: string;
  "Official Source (URL)"?: string;
  "Official Source (PDF)"?: string;
  // Nested mappings
  Questions?: string;
  "Jurisdictions Link"?: string;
  "Jurisdictions Alpha-3 Code"?: string;
  Jurisdictions?: string;
  "Region (from Jurisdictions)"?: string;
  Themes?: string;
  // Legacy fields for backwards compatibility
  themes?: string;
  "Text of the Relevant Legal Provisions"?: string;
  "Domestic Legal Provisions"?: string;
  "Related Questions"?: string;
  "Related Literature"?: string;
  "OUP Chapter"?: string;
  "Country Report"?: string;
}

/** Processed type with normalized fields */
export interface CourtDecision extends CourtDecisionResponse {
  hasEnglishQuoteTranslation: boolean;
}

/** Transform raw response to processed type */
export function processCourtDecision(
  raw: CourtDecisionResponse,
): CourtDecision {
  const themes = raw.themes || raw.Themes;
  const questions = raw.Questions;

  return {
    ...raw,
    "Case Title":
      raw["Case Title"] === "Not found"
        ? raw["Case Citation"]
        : raw["Case Title"],
    "Related Literature": themes,
    Date: formatDate(raw.Date),
    "Last Modified": formatDate(raw["Last Modified"] || raw.Created),
    Themes: themes,
    Questions: questions,
    "Related Questions": questions,
    "Publication Date ISO": formatDate(raw["Publication Date ISO"]),
    "Date of Judgment": formatDate(raw["Date of Judgment"]),
    hasEnglishQuoteTranslation: Boolean(
      raw["Translated Excerpt"] && raw["Translated Excerpt"].trim() !== "",
    ),
  };
}
