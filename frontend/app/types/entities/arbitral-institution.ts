import type { components } from "@/types/api-schema";

export type ArbitralInstitutionResponse =
  components["schemas"]["ArbitralInstitutionRecord"];
export type ArbitralInstitutionDetailResponse =
  components["schemas"]["ArbitralInstitutionDetail"];

export type ArbitralInstitution = ArbitralInstitutionDetailResponse & {
  displayTitle: string;
};

export function processArbitralInstitution(
  raw: ArbitralInstitutionDetailResponse,
): ArbitralInstitution {
  const derivedTitle =
    raw.institution || raw.abbreviation || String(raw.id || "");

  return {
    ...raw,
    displayTitle: derivedTitle,
  };
}
