import type { components } from "@/types/api-schema";

export type CourtDecisionResponse =
  components["schemas"]["CourtDecisionRecord"];
export type CourtDecisionDetailResponse =
  components["schemas"]["CourtDecisionDetail"];

export type CourtDecision = CourtDecisionDetailResponse & {
  hasEnglishQuoteTranslation: boolean;
  displayTitle: string;
};

const EXCLUDED_TITLES = new Set(["na", "not found", "n/a"]);

function isValidTitle(title: string | undefined | null): title is string {
  if (!title) return false;
  return !EXCLUDED_TITLES.has(title.toLowerCase());
}

export function processCourtDecision(
  raw: CourtDecisionDetailResponse,
): CourtDecision {
  const caseTitle =
    raw.caseTitle === "Not found" ? raw.caseCitation : raw.caseTitle;
  const displayTitle = isValidTitle(caseTitle)
    ? caseTitle
    : isValidTitle(raw.caseCitation)
      ? raw.caseCitation
      : String(raw.id || "");

  return {
    ...raw,
    caseTitle,
    hasEnglishQuoteTranslation: Boolean(
      raw.translatedExcerpt && raw.translatedExcerpt.trim() !== "",
    ),
    displayTitle,
  };
}
