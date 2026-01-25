/**
 * Shared UI component types
 */

/** Item structure for RelatedItemsList */
export interface RelatedItem {
  id: string;
  title: string;
}

/** Empty value behavior configuration */
export interface EmptyValueBehavior {
  action: "hide" | "display";
  fallback?: string;
}
