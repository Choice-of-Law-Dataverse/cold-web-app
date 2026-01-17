/**
 * Jurisdiction entity type definitions
 */

export interface JurisdictionResponse {
  id: string;
  Name: string;
  "Alpha-3 Code": string;
  Type?: string;
  Region?: string;
  "Legal Family"?: string;
  "Answer Coverage"?: number;
  "Jurisdiction Summary"?: string;
  "Jurisdictional Differentiator"?: string;
  Literature?: string;
  "OUP Chapter"?: string;
  "Related Data"?: string;
  alpha3Code?: string;
  hop1_relations?: {
    specialists?: Array<{ Specialist: string }>;
  };
}
