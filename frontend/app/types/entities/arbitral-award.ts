import type { components } from "@/types/api-schema";

export type ArbitralAwardResponse =
  components["schemas"]["ArbitralAwardRecord"];

export type ArbitralAward = ArbitralAwardResponse & {
  displayTitle: string;
  arbitralInstitution?: string;
  formattedJurisdictions: Array<{ name: string }>;
  formattedThemes: Array<{ theme: string }>;
};

export function processArbitralAward(
  raw: ArbitralAwardResponse,
): ArbitralAward {
  const derivedTitle = raw.caseNumber || String(raw.id || "");

  const arbitralInstitution = Array.isArray(raw.relatedArbitralInstitutions)
    ? raw.relatedArbitralInstitutions
        .map((inst) => inst?.Institution)
        .filter((v): v is string => Boolean(v && String(v).trim()))
        .join(", ")
    : undefined;

  const formattedJurisdictions = (() => {
    const list = raw.relatedJurisdictions;
    if (!Array.isArray(list)) return [];
    const names = list
      .map((j) => j?.Name)
      .filter((n): n is string => Boolean(n && String(n).trim()))
      .map((n) => String(n).trim());
    return [...new Set(names)].map((n) => ({ name: n }));
  })();

  const formattedThemes = (() => {
    const list = raw.relatedThemes;
    if (!Array.isArray(list)) return [];
    const themes = list
      .map((t) => t?.Theme)
      .filter((n): n is string => Boolean(n && String(n).trim()))
      .map((n) => String(n).trim());
    return [...new Set(themes)].map((t) => ({ theme: t }));
  })();

  return {
    ...raw,
    displayTitle: derivedTitle,
    arbitralInstitution,
    formattedJurisdictions,
    formattedThemes,
  };
}
