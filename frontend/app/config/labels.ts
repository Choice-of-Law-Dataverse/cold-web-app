/**
 * Label mappings for entity detail pages
 * Maps API field keys to display labels
 *
 * These objects are the source of truth for which fields to display.
 * `satisfies` ensures keys exist on entity types while preserving literal types.
 */

export const jurisdictionLabels = {
  jurisdictionSummary: "Summary",
  jurisdictionalDifferentiator: "Jurisdictional Differentiator",
  literature: "Related Literature",
  oupChapter: "OUP Chapter",
  relatedData: "Related Data",
} as const;

export const questionLabels = {
  question: "Question",
  answer: "Answer",
  moreInformation: "More Information",
  domesticLegalProvisions: "Source",
  oupBookQuote: "OUP Book Quote",
  courtDecisionsId: "Related Court Decisions",
  relatedLiterature: "Related Literature",
} as const;

export const courtDecisionLabels = {
  caseTitle: "Case Title",
  caseCitation: "Suggested Case Citation",
  publicationDateIso: "Publication Date",
  dateOfJudgment: "Judgment Date",
  instance: "Instance",
  abstract: "Abstract",
  relevantFacts: "Relevant Facts",
  pilProvisions: "PIL Provisions",
  domesticLegalProvisions: "Domestic Legal Provisions",
  textOfTheRelevantLegalProvisions: "Text of the Relevant Legal Provisions",
  choiceOfLawIssue: "Choice of Law Issue",
  courtSPosition: "Court's Position",
  quote: "Quote",
  originalText: "Full Text",
  relatedQuestions: "Related Questions",
  relatedLiterature: "Related Literature",
} as const;

export const literatureLabels = {
  title: "Title",
  author: "Author(s)",
  editor: "Editor(s)",
  publicationYear: "Year",
  publicationTitle: "Publication",
  publisher: "Publisher",
  abstractNote: "Abstract",
} as const;

export const domesticInstrumentLabels = {
  titleInEnglish: "Name",
  compatibility: "Compatible with",
  amendedBy: "Amended by",
  amends: "Amends",
  replaces: "Replaces",
  replacedBy: "Replaced by",
  officialTitle: "Official Title",
  abbreviation: "Abbreviation",
  date: "Date",
  entryIntoForce: "Entry Into Force",
  publicationDate: "Publication Date",
  domesticLegalProvisions: "Selected Provisions",
} as const;

export const regionalInstrumentLabels = {
  abbreviation: "Abbreviation",
  title: "Title",
  date: "Date",
  literature: "Related Literature",
  regionalLegalProvisions: "Selected Provisions",
} as const;

export const internationalInstrumentLabels = {
  name: "Title",
  date: "Date",
  specialists: "Specialists",
  literature: "Related Literature",
  selectedProvisions: "Selected Provisions",
} as const;

export const arbitralRuleLabels = {
  setOfRules: "Set of Rules",
  arbitralInstitution: "Arbitral Institutions",
  inForceFrom: "In Force From",
} as const;

export const arbitralAwardLabels = {
  caseNumber: "Case Number",
  arbitralInstitution: "Arbitral Institutions",
  source: "Source",
  year: "Year",
  natureOfTheAward: "Nature of the Award",
  context: "Context",
  seatTown: "Seat (Town)",
  awardSummary: "Award Summary",
} as const;

// Derive field types from labels (now narrow literal unions)
export type JurisdictionField = keyof typeof jurisdictionLabels;
export type QuestionField = keyof typeof questionLabels;
export type CourtDecisionField = keyof typeof courtDecisionLabels;
export type LiteratureField = keyof typeof literatureLabels;
export type DomesticInstrumentField = keyof typeof domesticInstrumentLabels;
export type RegionalInstrumentField = keyof typeof regionalInstrumentLabels;
export type InternationalInstrumentField =
  keyof typeof internationalInstrumentLabels;
export type ArbitralRuleField = keyof typeof arbitralRuleLabels;
export type ArbitralAwardField = keyof typeof arbitralAwardLabels;
