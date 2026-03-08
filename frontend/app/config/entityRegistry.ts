import type { TableName } from "@/types/api";
import type { RelatedItem } from "@/types/ui";
import {
  specialistLabels,
  courtDecisionLabels,
  questionLabels,
  literatureLabels,
  domesticInstrumentLabels,
  regionalInstrumentLabels,
  internationalInstrumentLabels,
  arbitralRuleLabels,
  arbitralAwardLabels,
  jurisdictionLabels,
  domesticLegalProvisionLabels,
  regionalLegalProvisionLabels,
  internationalLegalProvisionLabels,
} from "@/config/labels";
import {
  courtDecisionTooltips,
  questionTooltips,
  literatureTooltips,
  domesticInstrumentTooltips,
  regionalInstrumentTooltips,
  internationalInstrumentTooltips,
  jurisdictionTooltips,
} from "@/config/tooltips";
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
  labels: Record<string, string>;
  tooltips?: Record<string, string>;
  titleKey: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  process: (raw: any) => any;
  skipLabelKeys: Set<string>;
  relations: RelationConfig[];
  hasDetailPage?: boolean;
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
    labels: specialistLabels,
    titleKey: "specialist",
    process: processSpecialist,
    skipLabelKeys: new Set(),
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
  },
  "/court-decision": {
    table: "Court Decisions",
    labels: courtDecisionLabels,
    tooltips: courtDecisionTooltips,
    titleKey: "caseTitle",
    process: processCourtDecision,
    skipLabelKeys: new Set([
      "relatedQuestions",
      "relatedLiterature",
      "domesticLegalProvisions",
    ]),
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
  },
  "/question": {
    table: "Answers",
    labels: questionLabels,
    tooltips: questionTooltips,
    titleKey: "question",
    process: processQuestion,
    skipLabelKeys: new Set([
      "courtDecisionsId",
      "relatedLiterature",
      "domesticLegalProvisions",
    ]),
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
  },
  "/literature": {
    table: "Literature",
    labels: literatureLabels,
    tooltips: literatureTooltips,
    titleKey: "title",
    process: processLiterature,
    skipLabelKeys: new Set(),
    relations: [],
  },
  "/domestic-instrument": {
    table: "Domestic Instruments",
    labels: domesticInstrumentLabels,
    tooltips: domesticInstrumentTooltips,
    titleKey: "titleInEnglish",
    process: processDomesticInstrument,
    skipLabelKeys: new Set(["domesticLegalProvisions"]),
    relations: [],
  },
  "/regional-instrument": {
    table: "Regional Instruments",
    labels: regionalInstrumentLabels,
    tooltips: regionalInstrumentTooltips,
    titleKey: "title",
    process: processRegionalInstrument,
    skipLabelKeys: new Set(["regionalLegalProvisions", "literature"]),
    relations: [
      {
        relationKey: "literature",
        label: "Literature",
        basePath: "/literature",
        variant: "literature",
      },
    ],
  },
  "/international-instrument": {
    table: "International Instruments",
    labels: internationalInstrumentLabels,
    tooltips: internationalInstrumentTooltips,
    titleKey: "name",
    process: processInternationalInstrument,
    skipLabelKeys: new Set(["selectedProvisions", "specialists", "literature"]),
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
  },
  "/arbitral-rule": {
    table: "Arbitral Rules",
    labels: arbitralRuleLabels,
    titleKey: "setOfRules",
    process: processArbitralRule,
    skipLabelKeys: new Set(),
    relations: [],
  },
  "/arbitral-award": {
    table: "Arbitral Awards",
    labels: arbitralAwardLabels,
    titleKey: "caseNumber",
    process: processArbitralAward,
    skipLabelKeys: new Set(),
    relations: [],
  },
  "/jurisdiction": {
    table: "Jurisdictions",
    labels: jurisdictionLabels,
    tooltips: jurisdictionTooltips,
    titleKey: "name",
    process: processJurisdiction,
    skipLabelKeys: new Set(["literature", "relatedData"]),
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
  },
  "/domestic-legal-provision": {
    table: "Domestic Legal Provisions",
    labels: domesticLegalProvisionLabels,
    titleKey: "title",
    process: processDomesticLegalProvision,
    skipLabelKeys: new Set(),
    relations: [],
    hasDetailPage: false,
  },
  "/regional-legal-provision": {
    table: "Regional Legal Provisions",
    labels: regionalLegalProvisionLabels,
    titleKey: "title",
    process: processRegionalLegalProvision,
    skipLabelKeys: new Set(),
    relations: [],
    hasDetailPage: false,
  },
  "/international-legal-provision": {
    table: "International Legal Provisions",
    labels: internationalLegalProvisionLabels,
    titleKey: "title",
    process: processInternationalLegalProvision,
    skipLabelKeys: new Set(),
    relations: [],
    hasDetailPage: false,
  },
};

export function getEntityConfig(basePath: string): EntityConfig | undefined {
  return entityRegistry[basePath];
}
