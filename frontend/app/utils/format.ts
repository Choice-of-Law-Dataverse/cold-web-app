import { format } from "date-fns";

/**
 * Format date with special handling for Jan 1 (shows year only)
 */
export function formatDate(
  dateString: string | null | undefined,
): string | undefined {
  if (!dateString) return undefined;

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
export function extractYear(
  dateString: string | null | undefined,
): string | undefined {
  if (!dateString) return undefined;

  const date = new Date(dateString);
  return date.getFullYear().toString();
}

/**
 * Format date to year only
 */
export function formatYear(
  dateString: string | null | undefined,
): number | undefined {
  if (!dateString) return undefined;
  const date = new Date(dateString);
  return isNaN(date.getTime()) ? undefined : date.getFullYear();
}

/**
 * Format date for display (short format: "Jan 1, 2024")
 */
export function formatDateShort(dateString: string | null | undefined): string {
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

const DATE_DDMMYYYY = /^(\d{2})\.(\d{2})\.(\d{4})$/;

/**
 * Parse a date string into a UTC timestamp suitable for sorting.
 * Supports DD.MM.YYYY (used by some relation views) and any format
 * the native Date constructor accepts (ISO 8601, RFC 2822, etc.).
 * Returns null when the input is missing or unparseable.
 */
export function parseSortableDate(
  value: string | null | undefined,
): number | null {
  if (typeof value !== "string") return null;
  const trimmed = value.trim();
  if (!trimmed) return null;
  const dmy = DATE_DDMMYYYY.exec(trimmed);
  if (dmy) {
    const day = Number(dmy[1]);
    const month = Number(dmy[2]);
    const year = Number(dmy[3]);
    return Date.UTC(year, month - 1, day);
  }
  const time = new Date(trimmed).getTime();
  return Number.isNaN(time) ? null : time;
}
