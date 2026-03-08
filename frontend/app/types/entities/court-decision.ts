import type { components } from "@/types/api-schema";
import { formatDate } from "@/utils/format";

export type CourtDecisionResponse =
  components["schemas"]["CourtDecisionRecord"];
export type CourtDecisionDetailResponse =
  components["schemas"]["CourtDecisionDetail"];

export type CourtDecision = CourtDecisionDetailResponse & {
  hasEnglishQuoteTranslation: boolean;
  displayTitle: string;
  themes?: string;
  relatedQuestions?: string;
  domesticLegalProvisions?: string;
  relatedLiterature?: string;
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

  const themes = raw.relations.themes
    .map((t) => t.theme)
    .filter(Boolean)
    .join(", ");

  const relatedQuestions = raw.relations.questions
    .map((q) => q.coldId)
    .filter(Boolean)
    .join(",");

  const domesticLegalProvisions = raw.relations.domesticLegalProvisions
    .map((p) => p.coldId)
    .filter(Boolean)
    .join(",");

  return {
    ...raw,
    caseTitle,
    date: formatDate(raw.date),
    publicationDateIso: formatDate(raw.publicationDateIso),
    dateOfJudgment: formatDate(raw.dateOfJudgment),
    hasEnglishQuoteTranslation: Boolean(
      raw.translatedExcerpt && raw.translatedExcerpt.trim() !== "",
    ),
    displayTitle,
    themes: themes || undefined,
    relatedQuestions: relatedQuestions || undefined,
    domesticLegalProvisions: domesticLegalProvisions || undefined,
    relatedLiterature: raw.relations.literature.length > 0 ? "has" : undefined,
  };
}
