/**
 * Tooltip content for entity detail pages
 * Only fields that need tooltips are included (Partial)
 */

import type {
  JurisdictionField,
  QuestionField,
  CourtDecisionField,
  LiteratureField,
  DomesticInstrumentField,
  RegionalInstrumentField,
  InternationalInstrumentField,
} from "@/config/labels";

// Jurisdiction tooltips
export const jurisdictionTooltips: Partial<Record<JurisdictionField, string>> =
  {
    "Jurisdictional Differentiator":
      "Jurisdictional peculiarities, such as the judicial hierarchy. To be read before consulting jurisdictional information.",
    "Related Literature":
      "This button will open the CoLD search and return all literature pieces that are relevant for this topic.",
    "Related Data":
      "This button will provide links to related external data sources with relevant information about this jurisdiction.",
  };

// Question tooltips
export const questionTooltips: Partial<Record<QuestionField, string>> = {
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
    "This button will open the CoLD search and return all literature pieces that are relevant for this topic.",
};

// Court Decision tooltips
export const courtDecisionTooltips: Partial<
  Record<CourtDecisionField, string>
> = {
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
    "This button will open the CoLD search and return all literature pieces that are relevant for this topic.",
};

// Literature tooltips
export const literatureTooltips: Partial<Record<LiteratureField, string>> = {
  "Publication Year": "Year of publication.",
  Publisher: "Publishing house.",
};

// Domestic Instrument tooltips
export const domesticInstrumentTooltips: Partial<
  Record<DomesticInstrumentField, string>
> = {
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
};

// Regional Instrument tooltips
export const regionalInstrumentTooltips: Partial<
  Record<RegionalInstrumentField, string>
> = {
  Date: "Date when the instrument was enacted or came into force.",
  Specialists:
    "Academics who have published on or are otherwise associated with this instrument.",
  Literature:
    "This button will open the CoLD search and return all literature pieces that are relevant for this instrument.",
  "Regional Legal Provisions":
    "Key provisions within the instrument, selected for their relevance to choice of law.",
};

// International Instrument tooltips
export const internationalInstrumentTooltips: Partial<
  Record<InternationalInstrumentField, string>
> = {
  Date: "Date when the instrument was enacted or came into force.",
  Specialists:
    "Academics who have published on or are otherwise associated with this instrument.",
  Literature:
    "This button will open the CoLD search and return all literature pieces that are relevant for this instrument.",
  "Selected Provisions":
    "Key provisions within the instrument, selected for their relevance to choice of law.",
};

// Arbitral Rule and Arbitral Award have no tooltips in the original config
