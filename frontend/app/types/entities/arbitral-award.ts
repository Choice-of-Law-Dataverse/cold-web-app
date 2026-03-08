import type { components } from "@/types/api-schema";

export type ArbitralAwardResponse =
  components["schemas"]["ArbitralAwardRecord"];
export type ArbitralAwardDetailResponse =
  components["schemas"]["ArbitralAwardDetail"];

export type ArbitralAward = ArbitralAwardDetailResponse & {
  displayTitle: string;
  arbitralInstitution?: string;
  formattedJurisdictions: Array<{ name: string }>;
  formattedThemes: Array<{ theme: string }>;
};

export function processArbitralAward(
  raw: ArbitralAwardDetailResponse,
): ArbitralAward {
  const derivedTitle = raw.caseNumber || String(raw.id || "");

  const arbitralInstitution =
    raw.relations.arbitralInstitutions
      .map((inst) => inst.institution)
      .filter((v): v is string => Boolean(v && String(v).trim()))
      .join(", ") || undefined;

  const jurisdictionNames = raw.relations.jurisdictions
    .map((j) => j.name)
    .filter((n): n is string => Boolean(n && String(n).trim()))
    .map((n) => String(n).trim());
  const formattedJurisdictions = [...new Set(jurisdictionNames)].map((n) => ({
    name: n,
  }));

  const themeNames = raw.relations.themes
    .map((t) => t.theme)
    .filter((n): n is string => Boolean(n && String(n).trim()))
    .map((n) => String(n).trim());
  const formattedThemes = [...new Set(themeNames)].map((t) => ({ theme: t }));

  return {
    ...raw,
    displayTitle: derivedTitle,
    arbitralInstitution,
    formattedJurisdictions,
    formattedThemes,
  };
}
