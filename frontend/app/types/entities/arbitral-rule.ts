import type { components } from "@/types/api-schema";

export type ArbitralRuleResponse = components["schemas"]["ArbitralRuleRecord"];
export type ArbitralRuleDetailResponse =
  components["schemas"]["ArbitralRuleDetail"];

export type ArbitralRule = ArbitralRuleDetailResponse & {
  arbitralInstitution?: string;
};

export function processArbitralRule(
  raw: ArbitralRuleDetailResponse,
): ArbitralRule {
  const arbitralInstitution =
    raw.relations.arbitralInstitutions
      .map((inst) => inst.institution)
      .filter((v): v is string => Boolean(v && String(v).trim()))
      .join(", ") || undefined;

  return {
    ...raw,
    arbitralInstitution,
  };
}
