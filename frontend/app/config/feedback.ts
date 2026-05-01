const ENTITY_TYPE_LABELS: Record<string, string> = {
  court_decision: "Court Decision",
  domestic_instrument: "Domestic Instrument",
  regional_instrument: "Regional Instrument",
  international_instrument: "International Instrument",
  literature: "Literature",
  arbitral_award: "Arbitral Award",
  arbitral_rule: "Arbitral Rule",
  question: "Question",
  jurisdiction: "Jurisdiction",
};

const FEEDBACK_TYPE_LABELS: Record<string, string> = {
  improve: "Suggest Improvement",
  missing_data: "Missing Data",
  wrong_info: "Wrong Information",
  outdated: "Outdated",
  other: "Other",
};

export function entityTypeLabel(type: string): string {
  return ENTITY_TYPE_LABELS[type] || type;
}

export function feedbackTypeLabel(type: string): string {
  return FEEDBACK_TYPE_LABELS[type] || type;
}
