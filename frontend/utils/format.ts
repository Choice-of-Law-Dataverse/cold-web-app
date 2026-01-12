import { format } from "date-fns";

/**
 * Format date with special handling for Jan 1 (shows year only)
 */
export function formatDate(dateString: string | null): string | null {
  if (!dateString) return null;

  const date = new Date(dateString);

  const isFirstOfJanuary = date.getDate() === 1 && date.getMonth() === 0;

  if (isFirstOfJanuary) {
    return date.getFullYear().toString();
  }

  return date.toLocaleDateString("en-GB", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

/**
 * Extract year from date string
 */
export function extractYear(dateString: string | null): string | null {
  if (!dateString) return null;

  const date = new Date(dateString);
  return date.getFullYear().toString();
}

/**
 * Format date to year only
 */
export function formatYear(dateString: string | null): string | number {
  if (!dateString) return "";
  const date = new Date(dateString);
  return isNaN(date.getTime()) ? "" : date.getFullYear();
}

/**
 * Format date for display (short format: "Jan 1, 2024")
 */
export function formatDateShort(dateString: string | null): string {
  if (!dateString) return "—";
  try {
    return format(new Date(dateString), "MMM d, yyyy");
  } catch {
    return dateString;
  }
}

/**
 * Format date for display (long format: "January 1st, 2024")
 */
export function formatDateLong(dateString: string): string {
  try {
    return format(new Date(dateString), "PPP");
  } catch {
    return dateString;
  }
}
