// API Request Body Types for useApiClient composables
export { ApiError } from './errors'

/**
 * Base interface for table-based requests
 */
export interface BaseTableRequest {
  table: TableName
}

/**
 * Request body for fetching details by ID
 */
export interface DetailsByIdRequest extends BaseTableRequest {
  id: string | number
}

/**
 * Request body for full table queries
 */
export interface FullTableRequest extends BaseTableRequest {
  filters?: Array<{
    column: string
    value: string | number | boolean
  }>
}

/**
 * Filter object for search requests
 */
export interface SearchFilter {
  column: string
  values: string[]
}

/**
 * Browser info interface
 */
export interface BrowserInfo {
  userAgent: string
  platform: string
  language: string
  screenWidth: number
  screenHeight: number
}

/**
 * Search filters interface for the useSearch hook
 */
export interface SearchFilters {
  jurisdiction?: string
  theme?: string
  type?: string
  sortBy?: 'date' | 'relevance'
}

/**
 * Search parameters interface for the useSearch hook
 */
export interface SearchParams {
  query: string
  filters: SearchFilters
  page?: number
  pageSize?: number
  /**
   * Optional override to control query enablement.
   * When defined, useSearch will use this value for the `enabled` flag
   * instead of inferring from query/filters.
   */
  enabledOverride?: boolean
}

/**
 * Enhanced search request body with all fields
 */
export interface EnhancedSearchRequest {
  search_string: string
  filters: SearchFilter[]
  page: number
  page_size: number
  sort_by_date?: boolean
  ip_address?: string
  browser_info_navigator?: BrowserInfo
  browser_info_hint?: any
  hostname?: string
}

/**
 * Request body for search queries
 */
export interface SearchRequest {
  search_string: string
  filters: SearchFilter[]
  page?: number
  page_size?: number
  sort_by_date?: boolean
}

/**
 * Request body for jurisdiction count queries
 */
export interface JurisdictionCountRequest extends SearchRequest {
  // Inherits all SearchRequest properties
}

/**
 * Union type of all possible API request body types
 */
export type ApiRequestBody =
  | DetailsByIdRequest
  | FullTableRequest
  | SearchRequest
  | EnhancedSearchRequest
  | JurisdictionCountRequest

/**
 * Table names used in the API
 */
export type TableName =
  | 'Answers'
  | 'Court Decisions'
  | 'Domestic Instruments'
  | 'Domestic Legal Provisions'
  | 'International Instruments'
  | 'International Legal Provisions'
  | 'Jurisdictions'
  | 'Leading Cases'
  | 'Literature'
  | 'Questions'
  | 'Regional Instruments'
  | 'Regional Legal Provisions'
  | 'Specialists'

/**
 * Search filter column names
 */
export type FilterColumn =
  | 'jurisdictions'
  | 'themes'
  | 'tables'
  | 'type'
  | string // Allow other column names

/**
 * Search response interface
 */
export interface SearchResponse {
  results: any[]
  totalMatches: number
}

/**
 * API response wrapper (generic)
 */
export interface ApiResponse<T = any> {
  data?: T
  error?: string
  total_matches?: number
  results?: Record<string, any>
  [key: string]: any
}
