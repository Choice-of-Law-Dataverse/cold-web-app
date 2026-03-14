import type { components } from "@/types/api-schema";
import { joinArbitralInstitutions } from "@/utils/entityHelpers";

export type ArbitralRuleResponse = components["schemas"]["ArbitralRuleRecord"];
export type ArbitralRuleDetailResponse =
  components["schemas"]["ArbitralRuleDetail"];

export type ArbitralRule = ArbitralRuleDetailResponse & {
  arbitralInstitution?: string;
};

export function processArbitralRule(
  raw: ArbitralRuleDetailResponse,
): ArbitralRule {
  return {
    ...raw,
    arbitralInstitution: joinArbitralInstitutions(
      raw.relations.arbitralInstitutions,
    ),
  };
}
