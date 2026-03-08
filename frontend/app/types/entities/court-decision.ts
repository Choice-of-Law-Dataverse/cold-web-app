import type { components } from "@/types/api-schema";
import { formatDate } from "@/utils/format";

export type CourtDecisionResponse =
  components["schemas"]["CourtDecisionRecord"];

export type CourtDecision = CourtDecisionResponse & {
  hasEnglishQuoteTranslation: boolean;
  displayTitle: string;
};

const EXCLUDED_TITLES = new Set(["na", "not found", "n/a"]);

function isValidTitle(title: string | undefined | null): title is string {
  if (!title) return false;
  return !EXCLUDED_TITLES.has(title.toLowerCase());
}

export function processCourtDecision(
  raw: CourtDecisionResponse,
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
    date: formatDate(raw.date),
    lastModified: formatDate(raw.lastModified || raw.created),
    publicationDateIso: formatDate(raw.publicationDateIso),
    dateOfJudgment: formatDate(raw.dateOfJudgment),
    hasEnglishQuoteTranslation: Boolean(
      raw.translatedExcerpt && raw.translatedExcerpt.trim() !== "",
    ),
    displayTitle,
  };
}
