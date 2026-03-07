/**
 * Arbitral Award entity type definitions
 */

/** Raw API response */
export interface ArbitralAwardResponse {
  id: string;
  sourceTable?: string;
  rank?: number;
  ID?: string;
  recordId?: string;
  caseNumber?: string;
  Context?: string;
  awardSummary?: string;
  Year?: string;
  natureOfTheAward?: string;
  seatTown?: string;
  Source?: string;
  Created?: string;
  lastModified?: string;
  sortDate?: string;
  arbitralInstitutions?: string;
  arbitralInstitutionsAbbrev?: string;
  arbitralInstitutionsLink?: string;
  arbitralProvisionsArticles?: string;
  arbitralProvisionsLink?: string;
  courtDecisions?: string;
  courtDecisionsLink?: string;
  jurisdictions?: string;
  jurisdictionsAlpha3Code?: string;
  jurisdictionsLink?: string;
  themes?: string;
  awardTitle?: string;
  caseTitle?: string;
  Title?: string;
  Name?: string;
  related_arbitral_institutions?: Array<{ Institution?: string }>;
  related_jurisdictions?: Array<{ Name?: string }>;
  related_themes?: Array<{ Theme?: string }>;
}

/** Processed type with normalized fields */
export interface ArbitralAward extends ArbitralAwardResponse {
  Title: string;
  arbitralInstitution?: string;
  formattedJurisdictions: Array<{ Name: string }>;
  formattedThemes: Array<{ Theme: string }>;
}

/** Transform raw response to processed type */
export function processArbitralAward(
  raw: ArbitralAwardResponse,
): ArbitralAward {
  const derivedTitle =
    raw.awardTitle || raw.caseTitle || raw.Title || raw.Name || "";

  const arbitralInstitution = Array.isArray(raw.related_arbitral_institutions)
    ? raw.related_arbitral_institutions
        .map((inst) => inst?.Institution)
        .filter((v): v is string => Boolean(v && String(v).trim()))
        .join(", ")
    : undefined;

  const formattedJurisdictions = (() => {
    const list = raw.related_jurisdictions;
    if (!Array.isArray(list)) return [];
    const names = list
      .map((j) => j?.Name)
      .filter((n): n is string => Boolean(n && String(n).trim()))
      .map((n) => String(n).trim());
    return [...new Set(names)].map((name) => ({ Name: name }));
  })();

  const formattedThemes = (() => {
    const list = raw.related_themes;
    if (!Array.isArray(list)) return [];
    const themes = list
      .map((t) => t?.Theme)
      .filter((n): n is string => Boolean(n && String(n).trim()))
      .map((n) => String(n).trim());
    return [...new Set(themes)].map((theme) => ({ Theme: theme }));
  })();

  return {
    ...raw,
    Title: derivedTitle,
    arbitralInstitution,
    formattedJurisdictions,
    formattedThemes,
  };
}
