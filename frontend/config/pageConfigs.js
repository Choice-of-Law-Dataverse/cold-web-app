/**
 * Configuration for page sections and their display properties
 * Each page has its own configuration object with:
 * - keyLabelPairs: Array of {key, label} pairs defining the sections
 * - valueClassMap: Object mapping API keys to CSS classes for styling
 */
import tooltipLiteraturePublisher from "@/content/info_boxes/literature/publisher.md?raw";
import tooltipLiteratureYear from "@/content/info_boxes/literature/year.md?raw";

import tooltipJurisdictionJurisdictionalDifferentiator from "@/content/info_boxes/jurisdiction/jurisdictional_differentiator.md?raw";
import tooltipJurisdictionRelatedLiterature from "@/content/info_boxes/jurisdiction/related_literature.md?raw";
import tooltipJurisdictionRelatedData from "@/content/info_boxes/jurisdiction/related_data.md?raw";

import tooltipQuestion from "@/content/info_boxes/question/question.md?raw";
import tooltipAnswer from "@/content/info_boxes/question/answer.md?raw";
import tooltipQuestionRelatedLiterature from "@/content/info_boxes/question/related_literature.md?raw";
import tooltipSource from "@/content/info_boxes/question/source.md?raw";
import tooltipOUPBookQuote from "@/content/info_boxes/question/oup_book_quote.md?raw";
import tooltipRelatedCourtDecisions from "@/content/info_boxes/question/related_court_decisions.md?raw";
import { formatDate, formatYear } from "@/utils/format";

import tooltipAbbreviation from "@/content/info_boxes/domestic_instrument/abbreviation.md?raw";
import tooltipCompatibleWith from "@/content/info_boxes/domestic_instrument/compatible_with.md?raw";
import tooltipDomesticInstrumentDate from "@/content/info_boxes/domestic_instrument/date.md?raw";
import tooltipEntryIntoForce from "@/content/info_boxes/domestic_instrument/entry_into_force.md?raw";
import tooltipOfficialTitle from "@/content/info_boxes/domestic_instrument/official_title.md?raw";
import tooltipDomesticInstrumentPublicationDate from "@/content/info_boxes/domestic_instrument/publication_date.md?raw";
import tooltipDomesticInstrumentSelectedProvisions from "@/content/info_boxes/domestic_instrument/selected_provisions.md?raw";
import tooltipDomesticInstrumentTitle from "@/content/info_boxes/domestic_instrument/title.md?raw";

import tooltipRegionalInstrumentDate from "@/content/info_boxes/regional_instrument/date.md?raw";
import tooltipRegionalInstrumentRelatedLiterature from "@/content/info_boxes/regional_instrument/related_literature.md?raw";
import tooltipRegionalInstrumentSelectedProvisions from "@/content/info_boxes/regional_instrument/selected_provisions.md?raw";
import tooltipRegionalInstrumentSpecialists from "@/content/info_boxes/regional_instrument/specialists.md?raw";

import tooltipInternationalInstrumentDate from "@/content/info_boxes/international_instrument/date.md?raw";
import tooltipInternationalInstrumentRelatedLiterature from "@/content/info_boxes/international_instrument/related_literature.md?raw";
import tooltipInternationalInstrumentSelectedProvisions from "@/content/info_boxes/international_instrument/selected_provisions.md?raw";
import tooltipInternationalInstrumentSpecialists from "@/content/info_boxes/international_instrument/specialists.md?raw";

import tooltipAbstract from "@/content/info_boxes/court_decision/abstract.md?raw";
import tooltipCaseCitation from "@/content/info_boxes/court_decision/case_citation.md?raw";
import tooltipCaseTitle from "@/content/info_boxes/court_decision/case_title.md?raw";
import tooltipChoiceOfLawIssue from "@/content/info_boxes/court_decision/choice_of_law_issue.md?raw";
import tooltipCourtsPosition from "@/content/info_boxes/court_decision/courts_position.md?raw";
import tooltipDomesticLegalProvision from "@/content/info_boxes/court_decision/domestic_legal_provision.md?raw";
import tooltipInstance from "@/content/info_boxes/court_decision/instance.md?raw";
import tooltipJudgmentDate from "@/content/info_boxes/court_decision/judgment_date.md?raw";
import tooltipPILProvisions from "@/content/info_boxes/court_decision/pil_provisions.md?raw";
import tooltipPublicationDate from "@/content/info_boxes/court_decision/publication_date.md?raw";
import tooltipQuote from "@/content/info_boxes/court_decision/quote.md?raw";
import tooltipCourtDecisionRelatedLiterature from "@/content/info_boxes/court_decision/related_literature.md?raw";
import tooltipRelatedQuestions from "@/content/info_boxes/court_decision/related_questions.md?raw";
import tooltipRelevantFacts from "@/content/info_boxes/court_decision/relevant_facts.md?raw";
import tooltipTextRelevantLegalProvision from "@/content/info_boxes/court_decision/text_relevant_legal_provision.md?raw";

export const literatureConfig = {
  keyLabelPairs: [
    {
      key: "Title",
      label: "Title",
      emptyValueBehavior: { action: "display", fallback: "No title available" },
    },
    {
      key: "Author",
      label: "Author(s)",
      emptyValueBehavior: {
        action: "display",
        fallback: "No author available",
      },
    },
    {
      key: "Editor",
      label: "Editor(s)",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Publication Year",
      label: "Year",
      tooltip: tooltipLiteratureYear,
      emptyValueBehavior: { action: "display", fallback: "No year available" },
    },
    {
      key: "Publication Title",
      label: "Publication",
      emptyValueBehavior: {
        action: "display",
        fallback: "No publication available",
        shouldDisplay: (data) => data["Item Type"] !== "book",
      },
    },
    {
      key: "Publisher",
      label: "Publisher",
      tooltip: tooltipLiteraturePublisher,
      emptyValueBehavior: {
        action: "display",
        fallback: "No publisher available",
        shouldDisplay: (data) => data["Item Type"] === "book",
      },
    },
    {
      key: "Abstract Note",
      label: "Abstract",
      emptyValueBehavior: { action: "hide" },
    },
  ],
  valueClassMap: {
    Title: "result-value-medium",
    Author: "result-value-small",
    Editor: "result-value-small",
    "Publication Year": "result-value-small",
    "Publication Title": "result-value-small",
    Publisher: "result-value-small",
    Themes: "result-value-small",
    Jurisdictions: "result-value-small",
    "Related Literature": "result-value-small",
    "Abstract Note": "result-value-small whitespace-pre-line",
  },
};

export const jurisdictionConfig = {
  keyLabelPairs: [
    {
      key: "Jurisdiction Summary",
      label: "Summary",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Jurisdictional Differentiator",
      label: "Jurisdictional Differentiator",
      tooltip: tooltipJurisdictionJurisdictionalDifferentiator,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Related Literature",
      label: "Related Literature",
      tooltip: tooltipJurisdictionRelatedLiterature,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "OUP Chapter",
      label: "OUP Chapter",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Related Data",
      label: "Related Data",
      tooltip: tooltipJurisdictionRelatedData,
      emptyValueBehavior: { action: "hide" },
    },
  ],
  valueClassMap: {
    "Jurisdiction Summary": "prose",
    "Jurisdictional Differentiator": "prose",
    "Related Literature": "prose",
  },
};

export const questionConfig = {
  keyLabelPairs: [
    {
      key: "Question",
      label: "Question",
      tooltip: tooltipQuestion,
      emptyValueBehavior: {
        action: "display",
        fallback: "No question available",
      },
    },
    {
      key: "Answer",
      label: "Answer",
      tooltip: tooltipAnswer,
      emptyValueBehavior: {
        action: "display",
        fallback: "No answer available",
      },
    },
    {
      key: "More Information",
      label: "More Information",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Domestic Legal Provisions",
      label: "Source",
      tooltip: tooltipSource,
      emptyValueBehavior: {
        action: "display",
        fallback: "No source available",
      },
    },

    {
      key: "OUP Chapter",
      label: "OUP Chapter",
      emptyValueBehavior: { action: "show" },
    },
    {
      key: "OUP Book Quote",
      label: "OUP Book Quote",
      tooltip: tooltipOUPBookQuote,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Court Decisions ID",
      label: "Related Court Decisions",
      tooltip: tooltipRelatedCourtDecisions,
      emptyValueBehavior: {
        action: "display",
        fallback: "No related court decisions",
      },
    },
    {
      key: "Related Literature",
      label: "Related Literature",
      tooltip: tooltipQuestionRelatedLiterature,
      emptyValueBehavior: {
        action: "display",
        fallback: "No related literature",
      },
    },
    {
      key: "Country Report",
      label: "Country Report",
      emptyValueBehavior: {
        shouldDisplay: () => true, // Always display this slot
      },
    },
    {
      key: "Last Modified",
      label: "Last Updated",
      emptyValueBehavior: {
        action: "hide",
        shouldDisplay: (data) => {
          const lm = data && data["Last Modified"];
          if (typeof formatYear === "function") {
            return !!formatYear(lm);
          }
          return !!(lm && !isNaN(new Date(lm)));
        },
      },
      valueTransform: (val) =>
        typeof formatDate === "function" ? formatDate(val) : val,
    },
    {
      key: "Created",
      label: "Last Updated",
      emptyValueBehavior: {
        action: "hide",
        shouldDisplay: (data) => {
          const lm = data && data["Last Modified"];
          const created = data && data["Created"];
          if (typeof formatYear === "function") {
            return !formatYear(lm) && !!formatYear(created);
          }
          return (
            !(lm && !isNaN(new Date(lm))) &&
            !!(created && !isNaN(new Date(created)))
          );
        },
      },
      valueTransform: (val) =>
        typeof formatDate === "function" ? formatDate(val) : val,
    },
  ],
  valueClassMap: {
    Question: "result-value-medium",
    Answer: "result-value-large",
    "Domestic Legal Provisions": "result-value-small",
    Created: "result-value-small",
    "More Information": "result-value-small whitespace-pre-line",
    "OUP Book Quote": "result-value-small",
    "Court Decisions ID": "result-value-small",
    "Related Literature": "result-value-small",
    "OUP Chapter": "result-value-small",
    "Country Report": "result-value-small",
    "Last Modified": "result-value-small",
  },
};

export const legalInstrumentConfig = {
  keyLabelPairs: [
    {
      key: "Title (in English)",
      label: "Name",
      tooltip: tooltipDomesticInstrumentTitle,
      emptyValueBehavior: { action: "display", fallback: "No title available" },
    },
    {
      key: "Compatibility",
      label: "Compatible with",
      tooltip: tooltipCompatibleWith,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Amended by",
      label: "Amended by",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Amends",
      label: "Amends",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Replaces",
      label: "Replaces",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Replaced by",
      label: "Replaced by",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Official Title",
      label: "Official Title",
      tooltip: tooltipOfficialTitle,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Abbreviation",
      label: "Abbreviation",
      tooltip: tooltipAbbreviation,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Date",
      label: "Date",
      tooltip: tooltipDomesticInstrumentDate,
      emptyValueBehavior: {
        action: "display",
        fallback: "N/A",
        shouldHide: (data) => {
          return data && (data["Entry Into Force"] || data["Publication Date"]);
        },
      },
    },
    {
      key: "Entry Into Force",
      label: "Entry Into Force",
      tooltip: tooltipEntryIntoForce,
      emptyValueBehavior: { action: "hide" },
      valueTransform: (val) =>
        typeof formatDate === "function" ? formatDate(val) : val,
    },
    {
      key: "Publication Date",
      label: "Publication Date",
      tooltip: tooltipDomesticInstrumentPublicationDate,
      emptyValueBehavior: { action: "hide" },
      valueTransform: (val) =>
        typeof formatDate === "function" ? formatDate(val) : val,
    },

    {
      key: "Domestic Legal Provisions",
      label: "Selected Provisions",
      tooltip: tooltipDomesticInstrumentSelectedProvisions,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "OUP Chapter",
      label: "OUP Chapter",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Country Report",
      label: "Country Report",
      emptyValueBehavior: {
        shouldDisplay: () => true, // Always display this slot
      },
    },
  ],
  valueClassMap: {
    "Title (in English)": "result-value-medium",
    "Official Title": "result-value-small",
    Date: "result-value-small",
    Abbreviation: "result-value-small",
    "Entry Into Force": "result-value-small",
    "Publication Date": "result-value-small",
    "Domestic Legal Provisions": "result-value-small",
    "Compatible With the HCCH Principles?": "result-value-small",
    "Compatible With the UNCITRAL Model Law?": "result-value-small",
    "Amended by": "result-value-small",
    Amends: "result-value-small",
    Replaces: "result-value-small",
    "Replaced by": "result-value-small",
    Themes: "result-value-small",
    "Manual Tags": "result-value-small",
    "Related Literature": "result-value-small",
    "OUP Chapter": "result-value-small",
    "Country Report": "result-value-small",
  },
};

export const regionalInstrumentConfig = {
  keyLabelPairs: [
    {
      key: "Abbreviation",
      label: "Abbreviation",
      emptyValueBehavior: { action: "display", fallback: "No title available" },
    },
    {
      key: "Title",
      label: "Title",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Date",
      label: "Date",
      tooltip: tooltipRegionalInstrumentDate,
      emptyValueBehavior: { action: "hide" },
      valueTransform: (val) =>
        typeof formatDate === "function" ? formatDate(val) : val,
    },
    {
      key: "Specialists",
      label: "Specialists",
      tooltip: tooltipRegionalInstrumentSpecialists,
      emptyValueBehavior: {
        action: "display",
        fallback: "No specialists available",
      },
    },
    {
      key: "Literature",
      label: "Related Literature",
      tooltip: tooltipRegionalInstrumentRelatedLiterature,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "OUP Chapter",
      label: "OUP Chapter",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Regional Legal Provisions",
      label: "Selected Provisions",
      tooltip: tooltipRegionalInstrumentSelectedProvisions,
      emptyValueBehavior: { action: "display", fallback: "" },
    },
  ],
  valueClassMap: {
    Abbreviation: "result-value-medium",
    Title: "result-value-small",
    Date: "result-value-small",
    "Related Literature": "result-value-small",
    "OUP Chapter": "result-value-small",
    "Regional Legal Provisions": "result-value-small",
  },
};

export const internationalInstrumentConfig = {
  keyLabelPairs: [
    {
      key: "Name",
      label: "Title",
      emptyValueBehavior: { action: "display", fallback: "No title available" },
    },
    {
      key: "Date",
      label: "Date",
      tooltip: tooltipInternationalInstrumentDate,
      emptyValueBehavior: { action: "display", fallback: "N/A" },
      valueTransform: (val) =>
        typeof formatDate === "function" ? formatDate(val) : val,
    },
    {
      key: "Specialists",
      label: "Specialists",
      tooltip: tooltipInternationalInstrumentSpecialists,
      emptyValueBehavior: {
        action: "display",
        fallback: "No specialists available",
      },
    },
    {
      key: "Literature",
      label: "Related Literature",
      tooltip: tooltipInternationalInstrumentRelatedLiterature,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "OUP Chapter",
      label: "OUP Chapter",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Selected Provisions",
      label: "Selected Provisions",
      tooltip: tooltipInternationalInstrumentSelectedProvisions,
      emptyValueBehavior: { action: "display", fallback: "" },
    },
  ],
  valueClassMap: {
    Name: "result-value-medium",
    Date: "result-value-small",
    Specialists: "result-value-small",
    "Related Literature": "result-value-small",
    "OUP Chapter": "result-value-small",
    "Selected Provisions": "result-value-small",
  },
};
export const arbitralRuleConfig = {
  keyLabelPairs: [
    {
      key: "Set of Rules",
      label: "Set of Rules",
      emptyValueBehavior: { action: "display", fallback: "No title available" },
    },
    {
      key: "Arbitral Institutions",
      label: "Arbitral Institutions",
      emptyValueBehavior: {
        action: "display",
        fallback: "No institution available",
      },
    },
    {
      key: "In Force From",
      label: "In Force From",
      emptyValueBehavior: { action: "hide" },
      valueTransform: (val) =>
        typeof formatDate === "function" ? formatDate(val) : val,
    },
  ],
  valueClassMap: {
    "Set of Rules": "result-value-medium",
    "In Force From": "result-value-small",
    "Arbitral Institutions": "result-value-small",
  },
};
export const arbitralAwardConfig = {
  keyLabelPairs: [
    {
      key: "Case Number",
      label: "Case Number",
      emptyValueBehavior: { action: "display", fallback: "No title available" },
    },
    {
      key: "Arbitral Institutions",
      label: "Arbitral Institutions",
      emptyValueBehavior: {
        action: "display",
        fallback: "No institution available",
      },
    },
    {
      key: "Source",
      label: "Source",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Year",
      label: "Year",
      emptyValueBehavior: { action: "display", fallback: "hide" },
    },
    {
      key: "Nature of the Award",
      label: "Nature of the Award",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Context",
      label: "Context",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Seat (Town)",
      label: "Seat (Town)",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Award Summary",
      label: "Award Summary",
      emptyValueBehavior: { action: "hide" },
    },
  ],
  valueClassMap: {
    "Case Number": "result-value-medium",
    "Arbitral Institution": "result-value-small",
    Source: "result-value-small",
    Year: "result-value-small",
    "Nature of the Award": "result-value-small",
    Context: "result-value-small",
    "Seat (Town)": "result-value-small",
    "Award Summary": "result-value-small",
  },
};

export const courtDecisionConfig = {
  keyLabelPairs: [
    {
      key: "Case Title",
      label: "Case Title",
      tooltip: tooltipCaseTitle,
      emptyValueBehavior: {
        action: "display",
        fallback: "No case title available",
        getFallback: (data) => {
          if (!data) {
            return "No case citation available";
          }
          const title = data["Case Title"];
          return !title || title.trim() === "NA"
            ? data["Case Citation"] || "No case citation available"
            : title;
        },
      },
    },
    {
      key: "Case Citation",
      label: "Suggested Case Citation",
      tooltip: tooltipCaseCitation,
      emptyValueBehavior: {
        action: "display",
        fallback: "No case citation available",
      },
    },
    {
      key: "Publication Date ISO",
      label: "Publication Date",
      tooltip: tooltipPublicationDate,
      emptyValueBehavior: { action: "display", fallback: "No date available" },
    },
    {
      key: "Date of Judgment",
      label: "Judgment Date",
      tooltip: tooltipJudgmentDate,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Instance",
      label: "Instance",
      tooltip: tooltipInstance,
      emptyValueBehavior: {
        action: "display",
        fallback: "No instance information available",
      },
    },
    {
      key: "Abstract",
      label: "Abstract",
      tooltip: tooltipAbstract,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Relevant Facts",
      label: "Relevant Facts",
      tooltip: tooltipRelevantFacts,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "PIL Provisions",
      label: "PIL Provisions",
      tooltip: tooltipPILProvisions,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Domestic Legal Provisions",
      label: "Domestic Legal Provisions",
      tooltip: tooltipDomesticLegalProvision,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Text of the Relevant Legal Provisions",
      label: "Text of the Relevant Legal Provisions",
      tooltip: tooltipTextRelevantLegalProvision,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Choice of Law Issue",
      label: "Choice of Law Issue",
      tooltip: tooltipChoiceOfLawIssue,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Court's Position",
      label: "Court's Position",
      tooltip: tooltipCourtsPosition,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Quote",
      label: "Quote",
      tooltip: tooltipQuote,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Original Text",
      label: "Full Text",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Related Questions",
      label: "Related Questions",
      tooltip: tooltipRelatedQuestions,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Related Literature",
      label: "Related Literature",
      tooltip: tooltipCourtDecisionRelatedLiterature,
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "OUP Chapter",
      label: "OUP Chapter",
      emptyValueBehavior: { action: "hide" },
    },
    {
      key: "Country Report",
      label: "Country Report",
      emptyValueBehavior: {
        shouldDisplay: () => true, // Always display this slot
      },
    },
  ],
  valueClassMap: {
    "Case Title": "result-value-medium",
    "Publication Date ISO": "result-value-small",
    "Date of Judgment": "result-value-small",
    Instance: "result-value-small",
    Abstract: "result-value-small whitespace-pre-line",
    "Relevant Facts": "result-value-small whitespace-pre-line",
    "PIL Provisions": "result-value-small",
    "Text of the Relevant Legal Provisions":
      "result-value-small whitespace-pre-line",
    "Choice of Law Issue": "result-value-small whitespace-pre-line",
    "Court's Position": "result-value-small whitespace-pre-line",
    Quote: "result-value-small",
    "Case Citation": "result-value-small-citation",
    "Original Text": "result-value-small",
    "Related Literature": "result-value-small",
    "OUP Chapter": "result-value-small",
    "Related Questions": "result-value-small",
    "Domestic Legal Provisions": "result-value-small",
    "Country Report": "result-value-small",
  },
};

export const aboutNavLinks = [
  { label: "About CoLD", key: "about-cold", path: "/about/about-cold" },
  { label: "Team", key: "team", path: "/about/team" },
  { label: "Supporters", key: "supporters", path: "/about/supporters" },
  { label: "Endorsements", key: "endorsements", path: "/about/endorsements" },
  { label: "Press", key: "press", path: "/about/press" },
];

export const learnNavLinks = [
  {
    label: "Open Educational Resources",
    key: "open-educational-resources",
    path: "/learn/open-educational-resources",
  },
  { label: "FAQ", key: "faq", path: "/learn/faq" },
  { label: "Methodology", key: "methodology", path: "/learn/methodology" },
  { label: "Glossary", key: "glossary", path: "/learn/glossary" },
  { label: "Data Sets", key: "data-sets", path: "/learn/data-sets" },
];
