/**
 * Parses a jurisdiction string that may contain single or multiple jurisdictions.
 * Handles jurisdiction names that contain commas (e.g., "Congo, the Democratic Republic of the")
 *
 * Since this data comes from the backend, we trust it and simply handle comma-separated lists.
 * Multi-word jurisdiction names with commas are preserved as single entries.
 *
 * @param {string} jurisdictionString - The string to parse
 * @returns {string[]} - Array of jurisdiction names
 */
export function parseJurisdictionString(jurisdictionString) {
  // Threshold for determining if a string is a comma-separated list.
  // Set to 2 because jurisdiction names with a single comma (like "Congo, the Democratic Republic of the")
  // should be treated as single jurisdictions, while strings with 2+ commas are likely lists.
  const MIN_COMMAS_FOR_LIST = 2;

  if (!jurisdictionString || typeof jurisdictionString !== "string") {
    return [];
  }

  const trimmed = jurisdictionString.trim();
  if (!trimmed) {
    return [];
  }

  // Check if the string contains " and " which typically indicates multiple jurisdictions
  if (trimmed.includes(" and ")) {
    return trimmed
      .split(" and ")
      .map((part) => part.trim())
      .filter((part) => part);
  }

  // For comma-separated values, we need to be careful about jurisdiction names
  // that naturally contain commas (e.g., "Congo, the Democratic Republic of the")
  // If there are multiple commas or the pattern suggests a list, split it
  const commaCount = (trimmed.match(/,/g) || []).length;

  if (commaCount >= MIN_COMMAS_FOR_LIST) {
    // Multiple commas likely indicate a list of jurisdictions
    return [...new Set(trimmed.split(",").map((part) => part.trim()))];
  }

  // Single comma or no comma - treat as a single jurisdiction
  return [trimmed];
}
