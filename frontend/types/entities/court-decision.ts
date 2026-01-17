/**
 * Court Decision entity type definitions
 */

import { formatDate } from "@/utils/format";

/** Raw API response */
export interface CourtDecisionResponse {
  id: string;
  "Case Title"?: string;
  "Case Citation"?: string;
  "Publication Date ISO"?: string;
  "Date of Judgment"?: string;
  Instance?: string;
  Abstract?: string;
  "Relevant Facts"?: string;
  "PIL Provisions"?: string;
  "Domestic Legal Provisions"?: string;
  "Text of the Relevant Legal Provisions"?: string;
  "Choice of Law Issue"?: string;
  "Court's Position"?: string;
  Quote?: string;
  "Translated Excerpt"?: string;
  "Original Text"?: string;
  "Related Questions"?: string;
  "Related Literature"?: string;
  "OUP Chapter"?: string;
  "Country Report"?: string;
  "Official Source (PDF)"?: string;
  "Official Source (URL)"?: string;
  "Jurisdictions Alpha-3 Code"?: string;
  themes?: string;
  Questions?: string;
}

/** Processed type with normalized fields */
export interface CourtDecision extends CourtDecisionResponse {
  hasEnglishQuoteTranslation: boolean;
}

/** Transform raw response to processed type */
export function processCourtDecision(
  raw: CourtDecisionResponse,
): CourtDecision {
  const themes = raw.themes;
  const questions = raw.Questions;

  return {
    ...raw,
    "Case Title":
      raw["Case Title"] === "Not found" ? raw["Case Citation"] : raw["Case Title"],
    "Related Literature": themes,
    themes,
    "Case Citation": raw["Case Citation"],
    Questions: questions,
    "Related Questions": questions,
    "Jurisdictions Alpha-3 Code": raw["Jurisdictions Alpha-3 Code"],
    "Publication Date ISO": formatDate(raw["Publication Date ISO"] ?? null) ?? undefined,
    "Date of Judgment": formatDate(raw["Date of Judgment"] ?? null) ?? undefined,
    hasEnglishQuoteTranslation: Boolean(
      raw["Translated Excerpt"] && raw["Translated Excerpt"].trim() !== "",
    ),
  };
}
