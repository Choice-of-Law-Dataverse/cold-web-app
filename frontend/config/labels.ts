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
  "Jurisdiction Summary": "Summary",
  "Jurisdictional Differentiator": "Jurisdictional Differentiator",
  Literature: "Related Literature",
  "OUP Chapter": "OUP Chapter",
  "Related Data": "Related Data",
} as const satisfies Partial<Record<keyof JurisdictionResponse, string>>;

export const questionLabels = {
  Question: "Question",
  Answer: "Answer",
  "More Information": "More Information",
  "Domestic Legal Provisions": "Source",
  "OUP Chapter": "OUP Chapter",
  "OUP Book Quote": "OUP Book Quote",
  "Court Decisions ID": "Related Court Decisions",
  "Related Literature": "Related Literature",
} as const satisfies Partial<Record<keyof Question, string>>;

export const courtDecisionLabels = {
  "Case Title": "Case Title",
  "Case Citation": "Suggested Case Citation",
  "Publication Date ISO": "Publication Date",
  "Date of Judgment": "Judgment Date",
  Instance: "Instance",
  Abstract: "Abstract",
  "Relevant Facts": "Relevant Facts",
  "PIL Provisions": "PIL Provisions",
  "Domestic Legal Provisions": "Domestic Legal Provisions",
  "Text of the Relevant Legal Provisions":
    "Text of the Relevant Legal Provisions",
  "Choice of Law Issue": "Choice of Law Issue",
  "Court's Position": "Court's Position",
  Quote: "Quote",
  "Original Text": "Full Text",
  "Related Questions": "Related Questions",
  "Related Literature": "Related Literature",
  "OUP Chapter": "OUP Chapter",
} as const satisfies Partial<Record<keyof CourtDecision, string>>;

export const literatureLabels = {
  Title: "Title",
  Author: "Author(s)",
  Editor: "Editor(s)",
  "Publication Year": "Year",
  "Publication Title": "Publication",
  Publisher: "Publisher",
  "Abstract Note": "Abstract",
} as const satisfies Partial<Record<keyof LiteratureResponse, string>>;

export const domesticInstrumentLabels = {
  "Title (in English)": "Name",
  Compatibility: "Compatible with",
  "Amended by": "Amended by",
  Amends: "Amends",
  Replaces: "Replaces",
  "Replaced by": "Replaced by",
  "Official Title": "Official Title",
  Abbreviation: "Abbreviation",
  Date: "Date",
  "Entry Into Force": "Entry Into Force",
  "Publication Date": "Publication Date",
  "Domestic Legal Provisions": "Selected Provisions",
  "OUP Chapter": "OUP Chapter",
} as const satisfies Partial<Record<keyof DomesticInstrument, string>>;

export const regionalInstrumentLabels = {
  Abbreviation: "Abbreviation",
  Title: "Title",
  Date: "Date",
  Specialists: "Specialists",
  Literature: "Related Literature",
  "OUP Chapter": "OUP Chapter",
  "Regional Legal Provisions": "Selected Provisions",
} as const satisfies Partial<Record<keyof RegionalInstrument, string>>;

export const internationalInstrumentLabels = {
  Name: "Title",
  Date: "Date",
  Specialists: "Specialists",
  Literature: "Related Literature",
  "OUP Chapter": "OUP Chapter",
  "Selected Provisions": "Selected Provisions",
} as const satisfies Partial<Record<keyof InternationalInstrument, string>>;

export const arbitralRuleLabels = {
  "Set of Rules": "Set of Rules",
  "Arbitral Institutions": "Arbitral Institutions",
  "In Force From": "In Force From",
} as const satisfies Partial<Record<keyof ArbitralRule, string>>;

export const arbitralAwardLabels = {
  "Case Number": "Case Number",
  "Arbitral Institutions": "Arbitral Institutions",
  Source: "Source",
  Year: "Year",
  "Nature of the Award": "Nature of the Award",
  Context: "Context",
  "Seat (Town)": "Seat (Town)",
  "Award Summary": "Award Summary",
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
