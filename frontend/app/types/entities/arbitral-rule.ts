import type { components } from "@/types/api-schema";

export type ArbitralRuleResponse = components["schemas"]["ArbitralRuleRecord"];

export type ArbitralRule = ArbitralRuleResponse & {
  arbitralInstitution?: string;
};

export function processArbitralRule(raw: ArbitralRuleResponse): ArbitralRule {
  const arbitralInstitution = Array.isArray(raw.relatedArbitralInstitutions)
    ? raw.relatedArbitralInstitutions
        .map((inst) => inst?.Institution)
        .filter((v): v is string => Boolean(v && String(v).trim()))
        .join(", ")
    : undefined;

  return {
    ...raw,
    arbitralInstitution,
  };
}
