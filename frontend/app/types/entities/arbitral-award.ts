import type { components } from "@/types/api-schema";

export type ArbitralAwardResponse =
  components["schemas"]["ArbitralAwardRecord"];
export type ArbitralAwardDetailResponse =
  components["schemas"]["ArbitralAwardDetail"];

export type ArbitralAward = ArbitralAwardDetailResponse & {
  displayTitle: string;
  arbitralInstitution?: string;
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

  return {
    ...raw,
    displayTitle: derivedTitle,
    arbitralInstitution,
  };
}
