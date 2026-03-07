/**
 * Jurisdiction entity type definitions
 */

/** Raw API response */
export interface JurisdictionResponse {
  id: string;
  sourceTable?: string;
  coldId?: string;
  Name: string;
  alpha3Code: string;
  Type?: string;
  Region?: string;
  northSouthDivide?: string;
  jurisdictionalDifferentiator?: string;
  recordId?: string;
  Created?: string;
  lastModified?: string;
  jurisdictionSummary?: string;
  legalFamily?: string;
  answerCoverage?: number;
  irrelevant?: boolean;
  Done?: boolean;
  Literature?: string;
  oupChapter?: string;
  relatedData?: string;
  Specialists?: string;
  hop1_relations?: {
    specialists?: Array<{ Specialist: string }>;
  };
}
