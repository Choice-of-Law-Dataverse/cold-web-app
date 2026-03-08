import type { TableName } from "@/types/api";
import type { RelatedItem } from "@/types/ui";
import { processSpecialist } from "@/types/entities/specialist";
import { processCourtDecision } from "@/types/entities/court-decision";
import { processQuestion } from "@/types/entities/question";
import { processLiterature } from "@/types/entities/literature";
import { processDomesticInstrument } from "@/types/entities/domestic-instrument";
import { processRegionalInstrument } from "@/types/entities/regional-instrument";
import { processInternationalInstrument } from "@/types/entities/international-instrument";
import { processArbitralRule } from "@/types/entities/arbitral-rule";
import { processArbitralAward } from "@/types/entities/arbitral-award";
import { processJurisdiction } from "@/types/entities/jurisdiction";
import {
  processDomesticLegalProvision,
  processRegionalLegalProvision,
  processInternationalLegalProvision,
} from "@/types/entities/legal-provision";
import {
  courtDecisionTooltips,
  questionTooltips,
  literatureTooltips,
  domesticInstrumentTooltips,
  regionalInstrumentTooltips,
  internationalInstrumentTooltips,
  jurisdictionTooltips,
} from "@/config/tooltips";

export interface RelationConfig {
  relationKey: string;
  label: string;
  basePath: string;
  variant?: string;
}

export interface RelationRendererConfig {
  label: string;
  basePath: string;
  variant?: string;
}

export const RELATION_RENDERERS: Record<string, RelationRendererConfig> = {
  specialists: {
    label: "Specialists",
    basePath: "/specialist",
    variant: "specialist",
  },
  questions: {
    label: "Questions",
    basePath: "/question",
    variant: "question",
  },
  courtDecisions: {
    label: "Court Decisions",
    basePath: "/court-decision",
    variant: "court-decision",
  },
  domesticInstruments: {
    label: "Domestic Instruments",
    basePath: "/domestic-instrument",
    variant: "instrument",
  },
  domesticLegalProvisions: {
    label: "Domestic Legal Provisions",
    basePath: "/domestic-legal-provision",
  },
  regionalInstruments: {
    label: "Regional Instruments",
    basePath: "/regional-instrument",
    variant: "instrument",
  },
  regionalLegalProvisions: {
    label: "Regional Legal Provisions",
    basePath: "/regional-legal-provision",
  },
  internationalInstruments: {
    label: "International Instruments",
    basePath: "/international-instrument",
    variant: "instrument",
  },
  internationalLegalProvisions: {
    label: "International Legal Provisions",
    basePath: "/international-legal-provision",
  },
  arbitralAwards: {
    label: "Arbitral Awards",
    basePath: "/arbitral-award",
    variant: "arbitration",
  },
  arbitralRules: {
    label: "Arbitral Rules",
    basePath: "/arbitral-rule",
    variant: "arbitration",
  },
  literature: {
    label: "Literature",
    basePath: "/literature",
    variant: "literature",
  },
};

export interface EntityConfig {
  table: TableName;
  fieldOrder: string[];
  labelOverrides?: Record<string, string>;
  tooltips?: Record<string, string>;
  titleKey: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  process: (raw: any) => any;
  relations: RelationConfig[];
  hasDetailPage?: boolean;
  variant?: string;
}

type RelationItem = Record<string, unknown>;

export function mapRelationToItem(item: RelationItem): RelatedItem {
  const id = String(item.coldId || item.id || "");
  const title = String(
    item.caseTitle ||
      item.caseCitation ||
      item.title ||
      item.titleInEnglish ||
      item.officialTitle ||
      item.titleOfTheProvision ||
      item.article ||
      item.name ||
      item.specialist ||
      item.question ||
      item.setOfRules ||
      item.caseNumber ||
      item.abbreviation ||
      item.coldId ||
      item.id ||
      "",
  );
  const result: RelatedItem = { id, title };
  if (item.oupJdChapter) {
    result.badge = { label: "OUP", color: "var(--color-label-oup)" };
  }
  return result;
}

export const entityRegistry: Record<string, EntityConfig> = {
  "/specialist": {
    table: "Specialists",
    fieldOrder: ["specialist", "affiliation", "contact", "bio", "website"],
    labelOverrides: { specialist: "Name", bio: "Biography" },
    titleKey: "specialist",
    process: processSpecialist,
    relations: [
      {
        relationKey: "jurisdictions",
        label: "Jurisdictions",
        basePath: "/jurisdiction",
        variant: "jurisdiction",
      },
      {
        relationKey: "internationalInstruments",
        label: "International Instruments",
        basePath: "/international-instrument",
        variant: "instrument",
      },
      {
        relationKey: "literature",
        label: "Literature",
        basePath: "/literature",
        variant: "literature",
      },
    ],
    variant: "specialist",
  },
  "/court-decision": {
    table: "Court Decisions",
    fieldOrder: [
      "caseTitle",
      "caseCitation",
      "publicationDateIso",
      "dateOfJudgment",
      "instance",
      "abstract",
      "relevantFacts",
      "pilProvisions",
      "domesticLegalProvisions",
      "textOfTheRelevantLegalProvisions",
      "choiceOfLawIssue",
      "courtSPosition",
      "quote",
      "originalText",
    ],
    labelOverrides: {
      caseCitation: "Suggested Case Citation",
      publicationDateIso: "Publication Date",
      dateOfJudgment: "Judgment Date",
      pilProvisions: "PIL Provisions",
      courtSPosition: "Court's Position",
      originalText: "Full Text",
    },
    tooltips: courtDecisionTooltips,
    titleKey: "caseTitle",
    process: processCourtDecision,
    relations: [
      {
        relationKey: "questions",
        label: "Related Questions",
        basePath: "/question",
        variant: "question",
      },
      {
        relationKey: "literature",
        label: "Literature",
        basePath: "/literature",
        variant: "literature",
      },
    ],
    variant: "court-decision",
  },
  "/question": {
    table: "Answers",
    fieldOrder: [
      "question",
      "answer",
      "moreInformation",
      "domesticLegalProvisions",
      "oupBookQuote",
    ],
    labelOverrides: {
      domesticLegalProvisions: "Source",
      oupBookQuote: "OUP Book Quote",
    },
    tooltips: questionTooltips,
    titleKey: "question",
    process: processQuestion,
    relations: [
      {
        relationKey: "courtDecisions",
        label: "Related Court Decisions",
        basePath: "/court-decision",
        variant: "court-decision",
      },
      {
        relationKey: "literature",
        label: "Literature",
        basePath: "/literature",
        variant: "literature",
      },
    ],
    variant: "question",
  },
  "/literature": {
    table: "Literature",
    fieldOrder: [
      "title",
      "author",
      "editor",
      "publicationYear",
      "publicationTitle",
      "publisher",
      "abstractNote",
    ],
    labelOverrides: {
      author: "Author(s)",
      editor: "Editor(s)",
      publicationYear: "Year",
      publicationTitle: "Publication",
      abstractNote: "Abstract",
    },
    tooltips: literatureTooltips,
    titleKey: "title",
    process: processLiterature,
    relations: [],
    variant: "literature",
  },
  "/domestic-instrument": {
    table: "Domestic Instruments",
    fieldOrder: [
      "titleInEnglish",
      "compatibility",
      "amendedBy",
      "amends",
      "replaces",
      "replacedBy",
      "officialTitle",
      "abbreviation",
      "date",
      "entryIntoForce",
      "publicationDate",
      "domesticLegalProvisions",
    ],
    labelOverrides: {
      titleInEnglish: "Name",
      compatibility: "Compatible with",
      domesticLegalProvisions: "Selected Provisions",
    },
    tooltips: domesticInstrumentTooltips,
    titleKey: "titleInEnglish",
    process: processDomesticInstrument,
    relations: [],
    variant: "instrument",
  },
  "/regional-instrument": {
    table: "Regional Instruments",
    fieldOrder: ["abbreviation", "title", "date", "regionalLegalProvisions"],
    labelOverrides: {
      regionalLegalProvisions: "Selected Provisions",
    },
    tooltips: regionalInstrumentTooltips,
    titleKey: "title",
    process: processRegionalInstrument,
    relations: [
      {
        relationKey: "literature",
        label: "Literature",
        basePath: "/literature",
        variant: "literature",
      },
    ],
    variant: "instrument",
  },
  "/international-instrument": {
    table: "International Instruments",
    fieldOrder: ["name", "date", "selectedProvisions"],
    labelOverrides: { name: "Title" },
    tooltips: internationalInstrumentTooltips,
    titleKey: "name",
    process: processInternationalInstrument,
    relations: [
      {
        relationKey: "specialists",
        label: "Specialists",
        basePath: "/specialist",
        variant: "specialist",
      },
      {
        relationKey: "literature",
        label: "Literature",
        basePath: "/literature",
        variant: "literature",
      },
    ],
    variant: "instrument",
  },
  "/arbitral-rule": {
    table: "Arbitral Rules",
    fieldOrder: ["setOfRules", "arbitralInstitution", "inForceFrom"],
    labelOverrides: {
      setOfRules: "Set of Rules",
      arbitralInstitution: "Arbitral Institutions",
    },
    titleKey: "setOfRules",
    process: processArbitralRule,
    relations: [],
    variant: "arbitration",
  },
  "/arbitral-award": {
    table: "Arbitral Awards",
    fieldOrder: [
      "caseNumber",
      "arbitralInstitution",
      "source",
      "year",
      "natureOfTheAward",
      "context",
      "seatTown",
      "awardSummary",
    ],
    labelOverrides: {
      arbitralInstitution: "Arbitral Institutions",
      natureOfTheAward: "Nature of the Award",
      seatTown: "Seat (Town)",
    },
    titleKey: "caseNumber",
    process: processArbitralAward,
    relations: [],
    variant: "arbitration",
  },
  "/jurisdiction": {
    table: "Jurisdictions",
    fieldOrder: ["jurisdictionSummary", "jurisdictionalDifferentiator"],
    labelOverrides: { jurisdictionSummary: "Summary" },
    tooltips: jurisdictionTooltips,
    titleKey: "name",
    process: processJurisdiction,
    relations: [
      {
        relationKey: "specialists",
        label: "Specialists",
        basePath: "/specialist",
        variant: "specialist",
      },
      {
        relationKey: "domesticInstruments",
        label: "Domestic Instruments",
        basePath: "/domestic-instrument",
        variant: "instrument",
      },
      {
        relationKey: "courtDecisions",
        label: "Court Decisions",
        basePath: "/court-decision",
        variant: "court-decision",
      },
      {
        relationKey: "literature",
        label: "Literature",
        basePath: "/literature",
        variant: "literature",
      },
    ],
    variant: "jurisdiction",
  },
  "/domestic-legal-provision": {
    table: "Domestic Legal Provisions",
    fieldOrder: ["title", "englishText", "originalText"],
    labelOverrides: { title: "Article", englishText: "English Translation" },
    titleKey: "title",
    process: processDomesticLegalProvision,
    relations: [],
    hasDetailPage: false,
  },
  "/regional-legal-provision": {
    table: "Regional Legal Provisions",
    fieldOrder: ["title", "originalText"],
    labelOverrides: { title: "Provision", originalText: "Text" },
    titleKey: "title",
    process: processRegionalLegalProvision,
    relations: [],
    hasDetailPage: false,
  },
  "/international-legal-provision": {
    table: "International Legal Provisions",
    fieldOrder: ["title", "originalText"],
    labelOverrides: { title: "Provision", originalText: "Text" },
    titleKey: "title",
    process: processInternationalLegalProvision,
    relations: [],
    hasDetailPage: false,
  },
};

export function getEntityConfig(basePath: string): EntityConfig | undefined {
  return entityRegistry[basePath];
}
