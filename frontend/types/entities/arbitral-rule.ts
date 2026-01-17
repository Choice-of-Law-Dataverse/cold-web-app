/**
 * Arbitral Rule entity type definitions
 */

/** Raw API response */
export interface ArbitralRuleResponse {
  id: string;
  "Set of Rules"?: string;
  "Arbitral Institutions"?: string;
  "In Force From"?: string;
  related_arbitral_institutions?: Array<{ Institution?: string }>;
}

/** Processed type with normalized fields */
export interface ArbitralRule extends ArbitralRuleResponse {
  "Arbitral Institution"?: string;
}

/** Transform raw response to processed type */
export function processArbitralRule(raw: ArbitralRuleResponse): ArbitralRule {
  const arbitralInstitution = Array.isArray(raw.related_arbitral_institutions)
    ? raw.related_arbitral_institutions
        .map((inst) => inst?.Institution)
        .filter((v): v is string => Boolean(v && String(v).trim()))
        .join(", ")
    : undefined;

  return {
    ...raw,
    "Arbitral Institution": arbitralInstitution,
  };
}
