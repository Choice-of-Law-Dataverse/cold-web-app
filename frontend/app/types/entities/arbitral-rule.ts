export interface ArbitralRuleResponse {
  id: string;
  sourceTable?: string;
  rank?: number;
  ID?: string;
  recordId?: string;
  setOfRules?: string;
  inForceFrom?: string;
  officialSourceUrl?: string;
  Created?: string;
  lastModified?: string;
  arbitralInstitutions?: string;
  arbitralInstitutionsAbbrev?: string;
  arbitralInstitutionsLink?: string;
  arbitralProvisionsArticles?: string;
  arbitralProvisionsLink?: string;
  Jurisdictions?: string;
  jurisdictionsAlpha3Code?: string;
  jurisdictionsLink?: string;
  related_arbitral_institutions?: Array<{ Institution?: string }>;
}

export interface ArbitralRule extends ArbitralRuleResponse {
  arbitralInstitution?: string;
}

export function processArbitralRule(raw: ArbitralRuleResponse): ArbitralRule {
  const arbitralInstitution = Array.isArray(raw.related_arbitral_institutions)
    ? raw.related_arbitral_institutions
        .map((inst) => inst?.Institution)
        .filter((v): v is string => Boolean(v && String(v).trim()))
        .join(", ")
    : undefined;

  return {
    ...raw,
    arbitralInstitution,
  };
}
