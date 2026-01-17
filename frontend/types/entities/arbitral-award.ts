/**
 * Arbitral Award entity type definitions
 */

/** Raw API response */
export interface ArbitralAwardResponse {
  id: string;
  "Case Number"?: string;
  "Award Title"?: string;
  "Case Title"?: string;
  Title?: string;
  Name?: string;
  "Arbitral Institutions"?: string;
  Source?: string;
  Year?: string;
  "Nature of the Award"?: string;
  Context?: string;
  "Seat (Town)"?: string;
  "Award Summary"?: string;
  related_arbitral_institutions?: Array<{ Institution?: string }>;
  related_jurisdictions?: Array<{ Name?: string }>;
  related_themes?: Array<{ Theme?: string }>;
}

/** Processed type with normalized fields */
export interface ArbitralAward extends ArbitralAwardResponse {
  Title: string;
  "Arbitral Institution"?: string;
  formattedJurisdictions: Array<{ Name: string }>;
  formattedThemes: Array<{ Theme: string }>;
}

/** Transform raw response to processed type */
export function processArbitralAward(
  raw: ArbitralAwardResponse,
): ArbitralAward {
  const derivedTitle =
    raw["Award Title"] || raw["Case Title"] || raw.Title || raw.Name || "";

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
    "Arbitral Institution": arbitralInstitution,
    formattedJurisdictions,
    formattedThemes,
  };
}
