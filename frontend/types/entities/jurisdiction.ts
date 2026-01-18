/**
 * Jurisdiction entity type definitions
 */

/** Raw API response */
export interface JurisdictionResponse {
  id: string;
  source_table?: string;
  cold_id?: string;
  Name: string;
  "Alpha-3 Code": string;
  Type?: string;
  Region?: string;
  "North-South Divide"?: string;
  "Jurisdictional Differentiator"?: string;
  "Record ID"?: string;
  Created?: string;
  "Last Modified"?: string;
  "Jurisdiction Summary"?: string;
  "Legal Family"?: string;
  "Answer Coverage"?: number;
  "Irrelevant?"?: boolean;
  Done?: boolean;
  // Legacy fields
  Literature?: string;
  "OUP Chapter"?: string;
  "Related Data"?: string;
  alpha3Code?: string;
  hop1_relations?: {
    specialists?: Array<{ Specialist: string }>;
  };
}
