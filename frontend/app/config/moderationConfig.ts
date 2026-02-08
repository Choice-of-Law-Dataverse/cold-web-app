/**
 * Shared configuration for moderation categories
 */

export interface CategoryConfig {
  id: string;
  label: string;
}

export const MODERATION_CATEGORIES: CategoryConfig[] = [
  { id: "case-analyzer", label: "Case Analyzer" },
  { id: "court-decisions", label: "Court Decisions" },
  { id: "domestic-instruments", label: "Domestic Instruments" },
  { id: "regional-instruments", label: "Regional Instruments" },
  { id: "international-instruments", label: "International Instruments" },
  { id: "literature", label: "Literature" },
  { id: "feedback", label: "Entity Feedback" },
];

export const CATEGORY_LABELS: Record<string, string> = Object.fromEntries(
  MODERATION_CATEGORIES.map((cat) => [cat.id, cat.label]),
);

export function getCategoryLabel(categoryId: string): string {
  return CATEGORY_LABELS[categoryId] || categoryId;
}
