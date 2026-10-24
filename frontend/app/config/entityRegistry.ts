import type { EntityType, TableName } from "@/types/api";
import type { AnySearchResult, AnySearchResultKey } from "@/types/search";
import type { RelatedItem } from "@/types/ui";
import type { Specialist } from "@/types/entities/specialist";
import type { CourtDecision } from "@/types/entities/court-decision";
import type { Question } from "@/types/entities/question";
import type { Literature } from "@/types/entities/literature";
import type { DomesticInstrument } from "@/types/entities/domestic-instrument";
import type { RegionalInstrument } from "@/types/entities/regional-instrument";
import type { InternationalInstrument } from "@/types/entities/international-instrument";
import type { ArbitralRule } from "@/types/entities/arbitral-rule";
import type { ArbitralAward } from "@/types/entities/arbitral-award";
import type { ArbitralInstitution } from "@/types/entities/arbitral-institution";
import type { HcchAnswer } from "@/types/entities/hcch-answer";
import type { Jurisdiction } from "@/types/entities/jurisdiction";
import type {
  DomesticLegalProvision,
  RegionalLegalProvision,
  InternationalLegalProvision,
} from "@/types/entities/legal-provision";
import { processSpecialist } from "@/types/entities/specialist";
import { processCourtDecision } from "@/types/entities/court-decision";
import { processQuestion } from "@/types/entities/question";
import { processLiterature } from "@/types/entities/literature";
import { processDomesticInstrument } from "@/types/entities/domestic-instrument";
import { processRegionalInstrument } from "@/types/entities/regional-instrument";
import { processInternationalInstrument } from "@/types/entities/international-instrument";
import { processArbitralRule } from "@/types/entities/arbitral-rule";
import { processArbitralAward } from "@/types/entities/arbitral-award";
import { processArbitralInstitution } from "@/types/entities/arbitral-institution";
import { processHcchAnswer } from "@/types/entities/hcch-answer";
import { processJurisdiction } from "@/types/entities/jurisdiction";
import {
  processDomesticLegalProvision,
  processRegionalLegalProvision,
  processInternationalLegalProvision,
} from "@/types/entities/legal-provision";

export interface ProcessedEntityMap {
  "/specialist": Specialist;
  "/court-decision": CourtDecision;
  "/question": Question;
  "/literature": Literature;
  "/domestic-instrument": DomesticInstrument;
  "/regional-instrument": RegionalInstrument;
  "/international-instrument": InternationalInstrument;
  "/arbitral-rule": ArbitralRule;
  "/arbitral-award": ArbitralAward;
  "/arbitral-institution": ArbitralInstitution;
  "/hcch-answer": HcchAnswer;
  "/jurisdiction": Jurisdiction;
  "/domestic-legal-provision": DomesticLegalProvision;
  "/regional-legal-provision": RegionalLegalProvision;
  "/international-legal-provision": InternationalLegalProvision;
}

export type EntityBasePath = keyof ProcessedEntityMap;
export type ProcessedEntity = ProcessedEntityMap[EntityBasePath];

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
  jurisdictions: {
    label: "Jurisdictions",
    basePath: "/jurisdiction",
    variant: "jurisdiction",
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
    variant: "instrument",
  },
  regionalInstruments: {
    label: "Regional Instruments",
    basePath: "/regional-instrument",
    variant: "instrument",
  },
  regionalLegalProvisions: {
    label: "Regional Legal Provisions",
    basePath: "/regional-legal-provision",
    variant: "instrument",
  },
  internationalInstruments: {
    label: "International Instruments",
    basePath: "/international-instrument",
    variant: "instrument",
  },
  internationalLegalProvisions: {
    label: "International Legal Provisions",
    basePath: "/international-legal-provision",
    variant: "instrument",
  },
  arbitralAwards: {
    label: "Arbitral Awards",
    basePath: "/arbitral-award",
    variant: "arbitration",
  },
  arbitralInstitutions: {
    label: "Arbitral Institutions",
    basePath: "/arbitral-institution",
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

export interface SearchCardFieldImage {
  dataKey: AnySearchResultKey;
  src: string;
  alt: string;
  class?: string;
}

export interface SearchCardField {
  key: AnySearchResultKey;
  label?: string;
  fallback?: (data: AnySearchResult) => string;
  format?: "date" | "year";
  inlineImage?: SearchCardFieldImage;
}

export interface SearchCardPdf {
  sourceFields: AnySearchResultKey[];
  folderName: string;
}

export interface SearchCardConfig {
  fields: SearchCardField[];
  pdf?: SearchCardPdf;
  processData?: (data: AnySearchResult) => AnySearchResult;
}

export interface EntityConfig {
  table: TableName;
  singularLabel: string;
  /** Backend collection slug, as in `/entities/{slug}` and `/suggestions/{slug}`. */
  collection?: string;
  /** Entity type the backend accepts for reader feedback on this record. */
  feedbackType?: EntityType;
  fieldOrder: string[];
  labelOverrides?: Record<string, string>;
  titleKey: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  process: (raw: any) => any;
  contentComponentId?: string;
  excludeRelations?: string[];
  hasDetailPage?: boolean;
  hasIndexPage?: boolean;
  hasNewPage?: boolean;
  /** Whether `{basePath}/{coldId}/edit` lets readers suggest an edit. */
  hasEditPage?: boolean;
  variant?: string;
  searchCard?: SearchCardConfig;
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
      item.institution ||
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
    singularLabel: "Specialist",
    collection: "specialists",
    fieldOrder: ["specialist", "affiliation", "contact", "bio", "website"],
    labelOverrides: { specialist: "Name", bio: "Biography" },
    titleKey: "specialist",
    process: processSpecialist,
    contentComponentId: "SpecialistContent",
    variant: "specialist",
  },
  "/court-decision": {
    table: "Court Decisions",
    singularLabel: "Court Decision",
    collection: "court-decisions",
    feedbackType: "court_decision",
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
    titleKey: "caseTitle",
    process: processCourtDecision,
    contentComponentId: "CourtDecisionContent",
    excludeRelations: ["jurisdictions"],
    hasNewPage: true,
    variant: "court-decision",
    searchCard: {
      fields: [
        {
          key: "caseTitle",
          fallback: (data: AnySearchResult) =>
            String(("caseCitation" in data && data.caseCitation) || ""),
        },
        {
          key: "publicationDateIso",
          label: "Date",
          format: "year",
        },
        { key: "instance" },
        { key: "choiceOfLawIssue" },
      ],
      pdf: {
        sourceFields: ["officialSourcePdf", "sourcePdf"],
        folderName: "court-decisions",
      },
    },
  },
  "/question": {
    table: "Answers",
    singularLabel: "Question",
    collection: "questions",
    feedbackType: "question",
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
    titleKey: "question",
    process: processQuestion,
    contentComponentId: "QuestionContent",
    excludeRelations: ["questions"],
    hasIndexPage: false,
    variant: "question",
    searchCard: {
      fields: [
        { key: "question" },
        { key: "answer" },
        { key: "moreInformation" },
      ],
    },
  },
  "/domestic-instrument": {
    table: "Domestic Instruments",
    singularLabel: "Domestic Instrument",
    collection: "domestic-instruments",
    feedbackType: "domestic_instrument",
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
    titleKey: "titleInEnglish",
    process: processDomesticInstrument,
    contentComponentId: "DomesticInstrumentContent",
    excludeRelations: ["jurisdictions"],
    hasNewPage: true,
    variant: "instrument",
    searchCard: {
      fields: [
        { key: "titleInEnglish", label: "Name" },
        { key: "date" },
        { key: "abbreviation" },
      ],
      pdf: {
        sourceFields: ["officialSourcePdf", "sourcePdf"],
        folderName: "domestic-instruments",
      },
      processData: (data) => ({
        ...data,
        themes:
          "domesticLegalProvisionsThemes" in data
            ? String(data.domesticLegalProvisionsThemes)
            : data.themes,
      }),
    },
  },
  "/regional-instrument": {
    table: "Regional Instruments",
    singularLabel: "Regional Instrument",
    collection: "regional-instruments",
    feedbackType: "regional_instrument",
    fieldOrder: ["abbreviation", "title", "date", "regionalLegalProvisions"],
    labelOverrides: {
      regionalLegalProvisions: "Selected Provisions",
    },
    titleKey: "title",
    process: processRegionalInstrument,
    contentComponentId: "RegionalInstrumentContent",
    hasNewPage: true,
    variant: "instrument",
    searchCard: {
      fields: [
        { key: "abbreviation" },
        { key: "date", format: "date" },
        { key: "title" },
      ],
      pdf: {
        sourceFields: ["attachment"],
        folderName: "regional-instruments",
      },
    },
  },
  "/international-instrument": {
    table: "International Instruments",
    singularLabel: "International Instrument",
    collection: "international-instruments",
    feedbackType: "international_instrument",
    fieldOrder: ["name", "date", "selectedProvisions"],
    labelOverrides: { name: "Title" },
    titleKey: "name",
    process: processInternationalInstrument,
    contentComponentId: "InternationalInstrumentContent",
    hasNewPage: true,
    hasEditPage: true,
    variant: "instrument",
    searchCard: {
      fields: [
        { key: "name", label: "Title" },
        { key: "date", format: "date" },
      ],
      pdf: {
        sourceFields: ["officialSourcePdf", "sourcePdf", "attachment"],
        folderName: "international-instruments",
      },
    },
  },
  "/literature": {
    table: "Literature",
    singularLabel: "Literature",
    collection: "literature",
    feedbackType: "literature",
    fieldOrder: [
      "title",
      "itemType",
      "author",
      "editor",
      "contributor",
      "publicationYear",
      "publicationTitle",
      "publisher",
      "place",
      "doi",
      "abstractNote",
    ],
    labelOverrides: {
      author: "Author(s)",
      editor: "Editor(s)",
      contributor: "Contributor(s)",
      publicationYear: "Year",
      publicationTitle: "Publication",
      abstractNote: "Abstract",
      itemType: "Type",
      doi: "DOI",
    },
    titleKey: "title",
    process: processLiterature,
    contentComponentId: "LiteratureContent",
    hasNewPage: true,
    variant: "literature",
    searchCard: {
      fields: [
        {
          key: "title",
          inlineImage: {
            dataKey: "openAccess",
            src: "https://assets.cold.global/assets/Open_Access_logo_PLoS_transparent.svg",
            alt: "Open Access Logo",
            class: "ml-1 inline-flex w-3",
          },
        },
        { key: "author" },
        { key: "publicationYear", label: "Date" },
        { key: "publicationTitle" },
        { key: "publisher" },
      ],
    },
  },
  "/arbitral-rule": {
    table: "Arbitral Rules",
    singularLabel: "Arbitral Rule",
    collection: "arbitral-rules",
    feedbackType: "arbitral_rule",
    fieldOrder: ["setOfRules", "arbitralInstitution", "inForceFrom"],
    labelOverrides: {
      setOfRules: "Set of Rules",
      arbitralInstitution: "Arbitral Institutions",
    },
    titleKey: "setOfRules",
    process: processArbitralRule,
    variant: "arbitration",
    searchCard: {
      fields: [
        { key: "setOfRules" },
        { key: "arbitralInstitutions" },
        { key: "inForceFrom", format: "date" },
      ],
    },
  },
  "/arbitral-institution": {
    table: "Arbitral Institutions",
    singularLabel: "Arbitral Institution",
    collection: "arbitral-institutions",
    fieldOrder: ["institution", "abbreviation"],
    titleKey: "institution",
    process: processArbitralInstitution,
    excludeRelations: ["jurisdictions"],
    variant: "arbitration",
  },
  "/arbitral-award": {
    table: "Arbitral Awards",
    singularLabel: "Arbitral Award",
    collection: "arbitral-awards",
    feedbackType: "arbitral_award",
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
    excludeRelations: ["jurisdictions"],
    variant: "arbitration",
    searchCard: {
      fields: [
        {
          key: "arbitralInstitutions",
        },
        {
          key: "awardSummary",
        },
      ],
    },
  },
  "/hcch-answer": {
    table: "HCCH Answers",
    singularLabel: "HCCH Answer",
    fieldOrder: ["adaptedQuestion", "position"],
    labelOverrides: {
      adaptedQuestion: "Question",
      position: "Position",
    },
    titleKey: "adaptedQuestion",
    process: processHcchAnswer,
    excludeRelations: ["questions"],
    hasDetailPage: false,
    hasIndexPage: false,
  },
  "/jurisdiction": {
    table: "Jurisdictions",
    singularLabel: "Report",
    collection: "jurisdictions",
    feedbackType: "jurisdiction",
    fieldOrder: ["name", "jurisdictionSummary", "jurisdictionalDifferentiator"],
    labelOverrides: { jurisdictionSummary: "Summary" },
    titleKey: "name",
    process: processJurisdiction,
    contentComponentId: "JurisdictionContent",
    hasIndexPage: false,
    variant: "jurisdiction",
  },
  "/domestic-legal-provision": {
    table: "Domestic Legal Provisions",
    singularLabel: "Domestic Legal Provision",
    fieldOrder: [
      "article",
      "fullTextOfTheProvisionEnglishTranslation",
      "fullTextOfTheProvisionOriginalLanguage",
    ],
    labelOverrides: {
      article: "Article",
      fullTextOfTheProvisionEnglishTranslation: "English Translation",
      fullTextOfTheProvisionOriginalLanguage: "Original Text",
    },
    titleKey: "article",
    process: processDomesticLegalProvision,
    excludeRelations: ["jurisdictions"],
    hasDetailPage: false,
    hasIndexPage: false,
  },
  "/regional-legal-provision": {
    table: "Regional Legal Provisions",
    singularLabel: "Regional Legal Provision",
    fieldOrder: ["titleOfTheProvision", "fullText"],
    labelOverrides: {
      titleOfTheProvision: "Provision",
      fullText: "Text",
    },
    titleKey: "titleOfTheProvision",
    process: processRegionalLegalProvision,
    hasDetailPage: false,
    hasIndexPage: false,
  },
  "/international-legal-provision": {
    table: "International Legal Provisions",
    singularLabel: "International Legal Provision",
    fieldOrder: ["titleOfTheProvision", "fullText"],
    labelOverrides: {
      titleOfTheProvision: "Provision",
      fullText: "Text",
    },
    titleKey: "titleOfTheProvision",
    process: processInternationalLegalProvision,
    hasDetailPage: false,
    hasIndexPage: false,
  },
} satisfies Record<EntityBasePath, EntityConfig>;

export function getEntityConfig(basePath: string): EntityConfig | undefined {
  return entityRegistry[basePath];
}

const tableToBasePath = new Map<string, string>();
const labelToBasePath = new Map<string, string>();

const collectionToBasePath = new Map<string, string>();

for (const [basePath, config] of Object.entries(entityRegistry)) {
  tableToBasePath.set(config.table, basePath);
  labelToBasePath.set(config.singularLabel, basePath);
  if (config.collection) collectionToBasePath.set(config.collection, basePath);
}

export function getEntityConfigByTable(
  table: string,
): EntityConfig | undefined {
  const basePath = tableToBasePath.get(table);
  return basePath ? entityRegistry[basePath] : undefined;
}

export function getBasePathForTable(table: string): string | undefined {
  return tableToBasePath.get(table);
}

/** Base path for a backend collection slug such as `court-decisions`. */
export function getBasePathForCollection(
  collection: string,
): string | undefined {
  return collectionToBasePath.get(collection);
}

export function getEditPathForCard(
  cardType: string,
  coldId: string,
): string | undefined {
  const basePath = getBasePathForCard(cardType);
  if (!basePath || !entityRegistry[basePath]?.hasEditPage) return undefined;
  return `${basePath}/${encodeURIComponent(coldId)}/edit`;
}

/**
 * Feedback entity type for a page path such as `/court-decision/CD-1`, from
 * the entity whose base path is the first segment. Empty when the entity does
 * not accept feedback.
 */
export function getFeedbackTypeForPath(path: string): EntityType | "" {
  const segment = path.split("/")[1] ?? "";
  return getEntityConfig(`/${segment}`)?.feedbackType ?? "";
}

/** Entity types a reader can suggest a new record for, in registry order. */
export function getNewEntityTypes(): string[] {
  return Object.values(entityRegistry)
    .filter((config) => config.hasNewPage)
    .map((config) => config.singularLabel);
}

export function getBasePathForCard(cardType: string): string | undefined {
  return tableToBasePath.get(cardType) ?? labelToBasePath.get(cardType);
}

export function getIndexPathForCard(cardType: string): string | undefined {
  const basePath = getBasePathForCard(cardType);
  if (!basePath) return undefined;
  const config = entityRegistry[basePath];
  if (config?.hasIndexPage === false) return undefined;
  return basePath;
}

export function getNewPathForCard(cardType: string): string | undefined {
  const basePath = getBasePathForCard(cardType);
  if (!basePath) return undefined;
  const config = entityRegistry[basePath];
  if (!config?.hasNewPage) return undefined;
  return `${basePath}/new`;
}

const VARIANT_TO_LABEL_CLASS: Record<string, string> = {
  "court-decision": "label-court-decision",
  question: "label-question",
  instrument: "label-instrument",
  arbitration: "label-arbitration",
  literature: "label-literature",
  jurisdiction: "label-jurisdiction",
  specialist: "label-specialist",
};

export function getLabelColorClass(cardType: string): string {
  const basePath = getBasePathForCard(cardType);
  const config = basePath ? entityRegistry[basePath] : undefined;
  if (!config?.variant) return "";
  return VARIANT_TO_LABEL_CLASS[config.variant] ?? "";
}

export function getSingularLabel(cardType: string): string {
  const basePath = getBasePathForCard(cardType);
  const config = basePath ? entityRegistry[basePath] : undefined;
  return config?.singularLabel ?? cardType;
}

export function getTableName(cardType: string): string {
  const basePath = getBasePathForCard(cardType);
  const config = basePath ? entityRegistry[basePath] : undefined;
  return config?.table ?? cardType;
}

export function getLabelColorClassByVariant(variant: string): string {
  return VARIANT_TO_LABEL_CLASS[variant] ?? "";
}
