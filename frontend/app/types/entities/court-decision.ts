import { formatDate } from "@/utils/format";

export interface CourtDecisionResponse {
  id: string;
  sourceTable?: string;
  rank?: number;
  ID?: string;
  caseCitation?: string;
  caseTitle?: string;
  Instance?: string;
  Date?: string;
  Abstract?: string;
  Created?: string;
  recordId?: string;
  idNumber?: string;
  lastModified?: string;
  answersLink?: string;
  answersQuestion?: string;
  textOfTheRelevantLegalProvisions?: string;
  Quote?: string;
  caseRank?: string;
  englishTranslation?: string;
  choiceOfLawIssue?: string;
  courtSPosition?: string;
  translatedExcerpt?: string;
  relevantFacts?: string;
  dateOfJudgment?: string;
  pilProvisions?: string;
  originalText?: string;
  sortDate?: string;
  publicationDateIso?: string;
  officialSourceUrl?: string;
  officialSourcePdf?: string;
  questions?: string;
  jurisdictionsLink?: string;
  jurisdictionsAlpha3Code?: string;
  jurisdictions?: string;
  regionFromJurisdictions?: string;
  themes?: string;
  domesticLegalProvisions?: string;
  relatedQuestions?: string;
  relatedLiterature?: string;
  oupChapter?: string;
  countryReport?: string;
}

export interface CourtDecision extends CourtDecisionResponse {
  hasEnglishQuoteTranslation: boolean;
  displayTitle: string;
}

const EXCLUDED_TITLES = new Set(["na", "not found", "n/a"]);

function isValidTitle(title: string | undefined): title is string {
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
      : raw.id;

  return {
    ...raw,
    caseTitle,
    Date: formatDate(raw.Date),
    lastModified: formatDate(raw.lastModified || raw.Created),
    publicationDateIso: formatDate(raw.publicationDateIso),
    dateOfJudgment: formatDate(raw.dateOfJudgment),
    hasEnglishQuoteTranslation: Boolean(
      raw.translatedExcerpt && raw.translatedExcerpt.trim() !== "",
    ),
    displayTitle,
  };
}
