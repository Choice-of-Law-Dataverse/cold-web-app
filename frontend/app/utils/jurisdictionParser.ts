/**
 * Parses a jurisdiction string that may contain single or multiple jurisdictions.
 * Handles jurisdiction names that contain commas (e.g., "Congo, the Democratic Republic of the")
 *
 * Since this data comes from the backend, we trust it and simply handle comma-separated lists.
 * Multi-word jurisdiction names with commas are preserved as single entries.
 *
 * Strings with 2+ commas are treated as comma-separated lists; strings with 0–1 commas
 * are treated as a single jurisdiction name.
 *
 * @param jurisdictionString - The string to parse
 * @returns Array of jurisdiction names
 */
export function parseJurisdictionString(jurisdictionString: string): string[] {
  const MIN_COMMAS_FOR_LIST = 2;

  if (!jurisdictionString) {
    return [];
  }

  const trimmed = jurisdictionString.trim();
  if (!trimmed) {
    return [];
  }

  if (trimmed.includes(" | ")) {
    return trimmed
      .split(" | ")
      .map((part) => part.trim())
      .filter((part) => part);
  }

  if (trimmed.includes(" and ")) {
    return trimmed
      .split(" and ")
      .map((part) => part.trim())
      .filter((part) => part);
  }

  const commaCount = (trimmed.match(/,/g) || []).length;

  if (commaCount >= MIN_COMMAS_FOR_LIST) {
    return [...new Set(trimmed.split(",").map((part) => part.trim()))];
  }

  return [trimmed];
}
