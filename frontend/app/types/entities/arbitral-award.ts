import type { components } from "@/types/api-schema";
import { joinArbitralInstitutions } from "@/utils/entityHelpers";

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

  return {
    ...raw,
    displayTitle: derivedTitle,
    arbitralInstitution: joinArbitralInstitutions(
      raw.relations.arbitralInstitutions,
    ),
  };
}
