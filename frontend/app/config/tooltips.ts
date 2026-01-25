/**
 * Tooltip content for entity detail pages
 * Only fields that need tooltips are included (Partial)
 *
 * `satisfies` ensures keys exist on entity types while preserving literal types.
 */

import type { JurisdictionResponse } from "@/types/entities/jurisdiction";
import type { Question } from "@/types/entities/question";
import type { CourtDecision } from "@/types/entities/court-decision";
import type { LiteratureResponse } from "@/types/entities/literature";
import type { DomesticInstrument } from "@/types/entities/domestic-instrument";
import type { RegionalInstrument } from "@/types/entities/regional-instrument";
import type { InternationalInstrument } from "@/types/entities/international-instrument";

export const jurisdictionTooltips = {
  "Jurisdictional Differentiator":
    "Jurisdictional peculiarities, such as the judicial hierarchy. To be read before consulting jurisdictional information.",
  Literature:
    "Academic literature relevant to this jurisdiction's choice of law framework.",
} as const satisfies Partial<Record<keyof JurisdictionResponse, string>>;

export const questionTooltips = {
  Question: "Question pertaining to chosen topic and jurisdiction.",
  Answer:
    "Predetermined response mostly limited to 'Yes', 'No', 'Not applicable', or 'No data'. Not a detailed or explanatory answer.",
  "Domestic Legal Provisions":
    "Statutory provisions that are referred to in the 'More Information' section, and that the jurisdiction-specific response is based upon.",
  "OUP Book Quote":
    "The OUP Book Quote is a copy/paste reference to the relevant question from the jurisdiction-specific chapter in the book 'The Elgar Companion to the Hague Conference on Private International Law'.",
  "Court Decisions ID":
    "Court decisions that have addressed the same legal issue, according to our database.",
  "Related Literature":
    "Academic literature relevant to this question's topic.",
} as const satisfies Partial<Record<keyof Question, string>>;

export const courtDecisionTooltips = {
  "Case Title":
    "Extracted from the case citation; main information to identify the case.",
  "Case Citation": "Official and generally accepted citation of a case.",
  "Publication Date ISO":
    "Date of the decision's publication in the official reporter or official database of the respective jurisdiction.",
  "Date of Judgment":
    "Date on which the judgment was handed down. In some jurisdictions, this differs from the publication date.",
  Instance:
    "Position of the deciding court within the hierarchy of the judiciary. Generally speaking, first instance refers to courts of first instance, second instance courts of appeal, third instance courts of last resort.",
  Abstract: "Short summary of the case, similar to a headnote.",
  "Relevant Facts":
    "Concise description of the factual background of the case, emphasising the facts that are relevant for the choice of law issue.",
  "PIL Provisions":
    "PIL provisions referred to by the court. Click for more information on the provision.",
  "Domestic Legal Provisions":
    "Non-PIL provisions relevant for the choice of law analysis of the case.",
  "Text of the Relevant Legal Provisions":
    "Full text of the relevant legal provisions.",
  "Choice of Law Issue":
    "Describes the choice of law issue addressed by the court in the relevant area of private international law.",
  "Court's Position":
    "Court's analysis and conclusion as to the relevant choice of law issue.",
  Quote:
    "Direct quote from the decision related to the choice of law issue. Translations of a quote are provided in square brackets.",
  "Related Questions":
    "Questions in our database that the court decision addresses.",
  "Related Literature":
    "Academic literature relevant to this court decision's legal issues.",
} as const satisfies Partial<Record<keyof CourtDecision, string>>;

export const literatureTooltips = {
  "Publication Year": "Year of publication.",
  Publisher: "Publishing house.",
} as const satisfies Partial<Record<keyof LiteratureResponse, string>>;

export const domesticInstrumentTooltips = {
  "Title (in English)":
    "English translation or accepted name of the instrument, typically a statute or regulation.",
  Compatibility:
    "Statement as to whether an instrument is compatible with the HCCH Principles or UNCITRAL Model Law.",
  "Official Title": "Title of the instrument in the original language.",
  Abbreviation: "Commonly used abbreviation for this instrument.",
  Date: "Date of enactment, usually when signed into law.",
  "Entry Into Force": "Date on which the instrument came into effect.",
  "Publication Date":
    "Date of publication in the official reporter or gazette.",
  "Domestic Legal Provisions":
    "Link to provisions of a particular relevance to Choice of Law, including key articles or sections.",
} as const satisfies Partial<Record<keyof DomesticInstrument, string>>;

export const regionalInstrumentTooltips = {
  Date: "Date when the instrument was enacted or came into force.",
  Specialists:
    "Academics who have published on or are otherwise associated with this instrument.",
  Literature:
    "This button will open the CoLD search and return all literature pieces that are relevant for this instrument.",
  "Regional Legal Provisions":
    "Key provisions within the instrument, selected for their relevance to choice of law.",
} as const satisfies Partial<Record<keyof RegionalInstrument, string>>;

export const internationalInstrumentTooltips = {
  Date: "Date when the instrument was enacted or came into force.",
  Specialists:
    "Academics who have published on or are otherwise associated with this instrument.",
  Literature:
    "This button will open the CoLD search and return all literature pieces that are relevant for this instrument.",
  "Selected Provisions":
    "Key provisions within the instrument, selected for their relevance to choice of law.",
} as const satisfies Partial<Record<keyof InternationalInstrument, string>>;
