export interface CategoryConfig {
  id: string;
  label: string;
  icon: string;
  color: string;
}

export const MODERATION_CATEGORIES: CategoryConfig[] = [
  {
    id: "case-analyzer",
    label: "Case Analyzer",
    icon: "i-heroicons-cpu-chip",
    color: "var(--color-cold-purple)",
  },
  {
    id: "court-decisions",
    label: "Court Decisions",
    icon: "i-heroicons-scale",
    color: "var(--color-label-court-decision)",
  },
  {
    id: "domestic-instruments",
    label: "Domestic Instruments",
    icon: "i-heroicons-building-library",
    color: "var(--color-label-instrument)",
  },
  {
    id: "regional-instruments",
    label: "Regional Instruments",
    icon: "i-heroicons-globe-europe-africa",
    color: "var(--color-label-instrument)",
  },
  {
    id: "international-instruments",
    label: "International Instruments",
    icon: "i-heroicons-globe-alt",
    color: "var(--color-label-instrument)",
  },
  {
    id: "literature",
    label: "Literature",
    icon: "i-heroicons-book-open",
    color: "var(--color-label-literature)",
  },
  {
    id: "feedback",
    label: "Entity Feedback",
    icon: "i-heroicons-chat-bubble-left-right",
    color: "var(--color-cold-teal)",
  },
];

const CATEGORY_LABELS: Record<string, string> = Object.fromEntries(
  MODERATION_CATEGORIES.map((cat) => [cat.id, cat.label]),
);

export function getCategoryLabel(categoryId: string): string {
  return CATEGORY_LABELS[categoryId] || categoryId;
}
