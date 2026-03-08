/**
 * Tooltip content for entity detail pages
 * Only fields that need tooltips are included (Partial)
 *
 * `satisfies` ensures keys exist on entity types while preserving literal types.
 */

export const jurisdictionTooltips = {
  jurisdictionalDifferentiator:
    "Jurisdictional peculiarities, such as the judicial hierarchy. To be read before consulting jurisdictional information.",
  literature:
    "Academic literature relevant to this jurisdiction's choice of law framework.",
} as const;

export const questionTooltips = {
  question: "Question pertaining to chosen topic and jurisdiction.",
  answer:
    "Predetermined response mostly limited to 'Yes', 'No', 'Not applicable', or 'No data'. Not a detailed or explanatory answer.",
  domesticLegalProvisions:
    "Statutory provisions that are referred to in the 'More Information' section, and that the jurisdiction-specific response is based upon.",
  oupBookQuote:
    "The OUP Book Quote is a copy/paste reference to the relevant question from the jurisdiction-specific chapter in the book 'The Elgar Companion to the Hague Conference on Private International Law'.",
  courtDecisionsId:
    "Court decisions that have addressed the same legal issue, according to our database.",
  relatedLiterature: "Academic literature relevant to this question's topic.",
} as const;

export const courtDecisionTooltips = {
  caseTitle:
    "Extracted from the case citation; main information to identify the case.",
  caseCitation: "Official and generally accepted citation of a case.",
  publicationDateIso:
    "Date of the decision's publication in the official reporter or official database of the respective jurisdiction.",
  dateOfJudgment:
    "Date on which the judgment was handed down. In some jurisdictions, this differs from the publication date.",
  instance:
    "Position of the deciding court within the hierarchy of the judiciary. Generally speaking, first instance refers to courts of first instance, second instance courts of appeal, third instance courts of last resort.",
  abstract: "Short summary of the case, similar to a headnote.",
  relevantFacts:
    "Concise description of the factual background of the case, emphasising the facts that are relevant for the choice of law issue.",
  pilProvisions:
    "PIL provisions referred to by the court. Click for more information on the provision.",
  domesticLegalProvisions:
    "Non-PIL provisions relevant for the choice of law analysis of the case.",
  textOfTheRelevantLegalProvisions:
    "Full text of the relevant legal provisions.",
  choiceOfLawIssue:
    "Describes the choice of law issue addressed by the court in the relevant area of private international law.",
  courtSPosition:
    "Court's analysis and conclusion as to the relevant choice of law issue.",
  quote:
    "Direct quote from the decision related to the choice of law issue. Translations of a quote are provided in square brackets.",
  relatedQuestions:
    "Questions in our database that the court decision addresses.",
  relatedLiterature:
    "Academic literature relevant to this court decision's legal issues.",
} as const;

export const literatureTooltips = {
  publicationYear: "Year of publication.",
  publisher: "Publishing house.",
} as const;

export const domesticInstrumentTooltips = {
  titleInEnglish:
    "English translation or accepted name of the instrument, typically a statute or regulation.",
  compatibility:
    "Statement as to whether an instrument is compatible with the HCCH Principles or UNCITRAL Model Law.",
  officialTitle: "Title of the instrument in the original language.",
  abbreviation: "Commonly used abbreviation for this instrument.",
  date: "Date of enactment, usually when signed into law.",
  entryIntoForce: "Date on which the instrument came into effect.",
  publicationDate: "Date of publication in the official reporter or gazette.",
  domesticLegalProvisions:
    "Link to provisions of a particular relevance to Choice of Law, including key articles or sections.",
} as const;

export const regionalInstrumentTooltips = {
  date: "Date when the instrument was enacted or came into force.",
  literature:
    "This button will open the CoLD search and return all literature pieces that are relevant for this instrument.",
  regionalLegalProvisions:
    "Key provisions within the instrument, selected for their relevance to choice of law.",
} as const;

export const internationalInstrumentTooltips = {
  date: "Date when the instrument was enacted or came into force.",
  specialists:
    "Academics who have published on or are otherwise associated with this instrument.",
  literature:
    "This button will open the CoLD search and return all literature pieces that are relevant for this instrument.",
  selectedProvisions:
    "Key provisions within the instrument, selected for their relevance to choice of law.",
} as const;
