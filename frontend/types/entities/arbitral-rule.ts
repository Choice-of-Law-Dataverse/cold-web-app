/**
 * Arbitral Rule entity type definitions
 */

export interface ArbitralRuleResponse {
  id: string;
  "Set of Rules"?: string;
  "Arbitral Institutions"?: string;
  "In Force From"?: string;
  related_arbitral_institutions?: Array<{ Institution?: string }>;
}
