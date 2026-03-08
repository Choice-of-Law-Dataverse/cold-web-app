/**
 * Label mappings for entity detail pages
 * Maps API field keys to display labels
 *
 * These objects are the source of truth for which fields to display.
 * `satisfies` ensures keys exist on entity types while preserving literal types.
 */

import type { JurisdictionResponse } from "@/types/entities/jurisdiction";
import type { Question } from "@/types/entities/question";
import type { CourtDecision } from "@/types/entities/court-decision";
import type { LiteratureResponse } from "@/types/entities/literature";
import type { DomesticInstrument } from "@/types/entities/domestic-instrument";
import type { RegionalInstrument } from "@/types/entities/regional-instrument";
import type { InternationalInstrument } from "@/types/entities/international-instrument";
import type { ArbitralRule } from "@/types/entities/arbitral-rule";
import type { ArbitralAward } from "@/types/entities/arbitral-award";

export const jurisdictionLabels = {
  jurisdictionSummary: "Summary",
  jurisdictionalDifferentiator: "Jurisdictional Differentiator",
  Literature: "Related Literature",
  oupChapter: "OUP Chapter",
  relatedData: "Related Data",
} as const satisfies Partial<Record<keyof JurisdictionResponse, string>>;

export const questionLabels = {
  question: "Question",
  answer: "Answer",
  moreInformation: "More Information",
  domesticLegalProvisions: "Source",
  oupChapter: "OUP Chapter",
  oupBookQuote: "OUP Book Quote",
  courtDecisionsId: "Related Court Decisions",
  relatedLiterature: "Related Literature",
} as const satisfies Partial<Record<keyof Question, string>>;

export const courtDecisionLabels = {
  caseTitle: "Case Title",
  caseCitation: "Suggested Case Citation",
  publicationDateIso: "Publication Date",
  dateOfJudgment: "Judgment Date",
  Instance: "Instance",
  Abstract: "Abstract",
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
  oupChapter: "OUP Chapter",
} as const satisfies Partial<Record<keyof CourtDecision, string>>;

export const literatureLabels = {
  Title: "Title",
  Author: "Author(s)",
  Editor: "Editor(s)",
  publicationYear: "Year",
  publicationTitle: "Publication",
  Publisher: "Publisher",
  abstractNote: "Abstract",
} as const satisfies Partial<Record<keyof LiteratureResponse, string>>;

export const domesticInstrumentLabels = {
  titleInEnglish: "Name",
  Compatibility: "Compatible with",
  amendedBy: "Amended by",
  Amends: "Amends",
  Replaces: "Replaces",
  replacedBy: "Replaced by",
  officialTitle: "Official Title",
  Abbreviation: "Abbreviation",
  Date: "Date",
  entryIntoForce: "Entry Into Force",
  publicationDate: "Publication Date",
  domesticLegalProvisions: "Selected Provisions",
  oupChapter: "OUP Chapter",
} as const satisfies Partial<Record<keyof DomesticInstrument, string>>;

export const regionalInstrumentLabels = {
  abbreviation: "Abbreviation",
  title: "Title",
  date: "Date",
  specialists: "Specialists",
  literature: "Related Literature",
  oupChapter: "OUP Chapter",
  regionalLegalProvisions: "Selected Provisions",
} as const satisfies Partial<Record<keyof RegionalInstrument, string>>;

export const internationalInstrumentLabels = {
  name: "Title",
  date: "Date",
  specialists: "Specialists",
  literature: "Related Literature",
  oupChapter: "OUP Chapter",
  selectedProvisions: "Selected Provisions",
} as const satisfies Partial<Record<keyof InternationalInstrument, string>>;

export const arbitralRuleLabels = {
  setOfRules: "Set of Rules",
  arbitralInstitutions: "Arbitral Institutions",
  inForceFrom: "In Force From",
} as const satisfies Partial<Record<keyof ArbitralRule, string>>;

export const arbitralAwardLabels = {
  caseNumber: "Case Number",
  arbitralInstitutions: "Arbitral Institutions",
  Source: "Source",
  Year: "Year",
  natureOfTheAward: "Nature of the Award",
  Context: "Context",
  seatTown: "Seat (Town)",
  awardSummary: "Award Summary",
} as const satisfies Partial<Record<keyof ArbitralAward, string>>;

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
