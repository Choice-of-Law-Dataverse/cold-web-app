/**
 * Arbitral Rule entity type definitions
 */

/** Raw API response */
export interface ArbitralRuleResponse {
  id: string;
  source_table?: string;
  rank?: number;
  ID?: string;
  "Record ID"?: string;
  "Set of Rules"?: string;
  "In Force From"?: string;
  "Official Source (URL)"?: string;
  Created?: string;
  "Last Modified"?: string;
  // Nested mappings
  "Arbitral Institutions"?: string;
  "Arbitral Institutions Abbrev"?: string;
  "Arbitral Institutions Link"?: string;
  "Arbitral Provisions (Articles)"?: string;
  "Arbitral Provisions Link"?: string;
  Jurisdictions?: string;
  "Jurisdictions Alpha-3 Code"?: string;
  "Jurisdictions Link"?: string;
  // Legacy fields
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
