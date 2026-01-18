// API Request Body Types for useApiClient composables
// Entity response type imports for TableResponseMap
import type { AnswerResponse } from "./entities/answer";
import type { ArbitralAwardResponse } from "./entities/arbitral-award";
import type { ArbitralRuleResponse } from "./entities/arbitral-rule";
import type { CourtDecisionResponse } from "./entities/court-decision";
import type { DomesticInstrumentResponse } from "./entities/domestic-instrument";
import type { InternationalInstrumentResponse } from "./entities/international-instrument";
import type { JurisdictionResponse } from "./entities/jurisdiction";
import type {
  DomesticLegalProvisionResponse,
  InternationalLegalProvisionResponse,
  RegionalLegalProvisionResponse,
} from "./entities/legal-provision";
import type { LiteratureResponse } from "./entities/literature";
import type { QuestionResponse } from "./entities/question";
import type { RegionalInstrumentResponse } from "./entities/regional-instrument";

export { ApiError } from "./errors";

/**
 * Question item data structure as returned from API
 */
export interface QuestionItem {
  "CoLD ID"?: string;
  ID?: string;
  Question: string;
  Themes?: string;
  [key: string]: unknown;
}

/**
 * Answer item data structure as returned from API
 */
export interface AnswerItem {
  [key: string]: string | unknown;
}

/**
 * Processed question with answer data
 */
export interface QuestionWithAnswer {
  id: string;
  question: string;
  theme?: string;
  answer: string;
  answerLink: string;
  level: number;
  hasExpand: boolean;
  expanded: boolean;
  parentId: string | null;
}

/**
 * Base interface for table-based requests
 */
export interface BaseTableRequest {
  table: TableName;
}

/**
 * Request body for fetching details by ID
 */
export interface DetailsByIdRequest extends BaseTableRequest {
  id: string | number;
}

/**
 * Filter for full table queries
 */
export interface FullTableFilter {
  column: string;
  value: string | number | boolean;
}

/**
 * Request body for full table queries
 */
export interface FullTableRequest extends BaseTableRequest {
  filters?: FullTableFilter[];
}

/**
 * Filter object for search requests
 */
export interface SearchFilter {
  column: string;
  values: string[];
}

/**
 * Browser info interface
 */
export interface BrowserInfo {
  userAgent: string;
  platform: string;
  language: string;
  screenWidth: number;
  screenHeight: number;
}

/**
 * Search filters interface for the useSearch hook
 */
export interface SearchFilters {
  jurisdiction?: string;
  theme?: string;
  type?: string;
  sortBy?: "date" | "relevance";
}

/**
 * Search parameters interface for the useSearch hook
 */
export interface SearchParams {
  query: string;
  filters: SearchFilters;
  page?: number;
  pageSize?: number;
  /**
   * Optional override to control query enablement.
   * When defined, useSearch will use this value for the `enabled` flag
   * instead of inferring from query/filters.
   */
  enabledOverride?: boolean;
}

/**
 * Enhanced search request body with all fields
 */
export interface EnhancedSearchRequest {
  search_string: string;
  filters: SearchFilter[];
  page: number;
  page_size: number;
  sort_by_date?: boolean;
  ip_address?: string;
  browser_info_navigator?: BrowserInfo;
  browser_info_hint?: Record<string, unknown>;
  hostname?: string;
}

/**
 * Request body for search queries
 */
export interface SearchRequest {
  search_string: string;
  filters: SearchFilter[];
  page?: number;
  page_size?: number;
  sort_by_date?: boolean;
}

/**
 * Request body for jurisdiction count queries
 */
export interface JurisdictionCountRequest extends SearchRequest {
  table?: TableName;
}

/**
 * Union type of all possible API request body types
 */
export type ApiRequestBody =
  | DetailsByIdRequest
  | FullTableRequest
  | SearchRequest
  | EnhancedSearchRequest
  | JurisdictionCountRequest;

/**
 * Table names used in the API
 */
export type TableName =
  | "Answers"
  | "Arbitral Awards"
  | "Arbitral Rules"
  | "Court Decisions"
  | "Domestic Instruments"
  | "Domestic Legal Provisions"
  | "International Instruments"
  | "International Legal Provisions"
  | "Jurisdictions"
  | "Leading Cases"
  | "Literature"
  | "Questions"
  | "Regional Instruments"
  | "Regional Legal Provisions"
  | "Specialists";

/**
 * Maps table names to their corresponding response types.
 * Used to provide type safety for filters and query results.
 */
export type TableResponseMap = {
  Answers: AnswerResponse;
  "Arbitral Awards": ArbitralAwardResponse;
  "Arbitral Rules": ArbitralRuleResponse;
  "Court Decisions": CourtDecisionResponse;
  "Domestic Instruments": DomesticInstrumentResponse;
  "Domestic Legal Provisions": DomesticLegalProvisionResponse;
  "International Instruments": InternationalInstrumentResponse;
  "International Legal Provisions": InternationalLegalProvisionResponse;
  Jurisdictions: JurisdictionResponse;
  "Leading Cases": CourtDecisionResponse; // Alias: Leading Cases = Court Decisions with Case Rank filter
  Literature: LiteratureResponse;
  Questions: QuestionResponse;
  "Regional Instruments": RegionalInstrumentResponse;
  "Regional Legal Provisions": RegionalLegalProvisionResponse;
  Specialists: Record<string, unknown>; // Not used with full_table endpoint
};

/**
 * Type-safe filter for a specific table.
 * The column must be a key from the table's response type.
 */
export type TypedFilter<T extends TableName> = {
  column: keyof TableResponseMap[T] & string;
  value: string | number | boolean;
};

/**
 * Search filter column names
 */
export type FilterColumn =
  | "jurisdictions"
  | "themes"
  | "tables"
  | "type"
  | string;

/**
 * Search response interface
 */
export interface SearchResponse {
  results: Record<string, unknown>[];
  totalMatches: number;
}

/**
 * Jurisdiction with answer coverage statistics
 */
export interface JurisdictionWithAnswerCoverage {
  id: number;
  Name: string;
  "Alpha-3 Code": string;
  "Answer Coverage": number;
  [key: string]: unknown; // Allows for additional jurisdiction fields
}

/**
 * Jurisdiction count statistics
 */
export interface JurisdictionCount {
  jurisdiction: string;
  n: number;
}

/**
 * API response wrapper (generic)
 */
export interface ApiResponse<T = unknown> {
  data?: T;
  error?: string;
  total_matches?: number;
  results?: Record<string, unknown>;
  [key: string]: unknown;
}
