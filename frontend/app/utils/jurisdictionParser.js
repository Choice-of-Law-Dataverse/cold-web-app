import jurisdictionsData from "@/assets/jurisdictions-data.json";

/**
 * Creates a set of all known jurisdiction names (lowercase) for fast lookup
 */
const knownJurisdictions = new Set(
  jurisdictionsData.flatMap((j) => j.name.map((n) => n.toLowerCase())),
);

/**
 * Parses a jurisdiction string that may contain single or multiple jurisdictions.
 * Handles jurisdiction names that contain commas (e.g., "Congo, the Democratic Republic of the")
 *
 * @param {string} jurisdictionString - The string to parse
 * @returns {string[]} - Array of jurisdiction names
 */
export function parseJurisdictionString(jurisdictionString) {
  if (!jurisdictionString || typeof jurisdictionString !== "string") {
    return [];
  }

  const trimmed = jurisdictionString.trim();
  if (!trimmed) {
    return [];
  }

  // First, check if the entire string is a known jurisdiction
  if (knownJurisdictions.has(trimmed.toLowerCase())) {
    return [trimmed];
  }

  // If not, try splitting by comma and validate each part
  const parts = trimmed.split(",").map((part) => part.trim());

  // Check if all parts are valid jurisdiction names
  const allPartsValid = parts.every((part) =>
    knownJurisdictions.has(part.toLowerCase()),
  );

  if (allPartsValid) {
    // All parts are valid jurisdictions, so it's a comma-separated list
    return [...new Set(parts)];
  }

  // If splitting by comma doesn't produce valid jurisdictions,
  // treat the entire string as a single jurisdiction name
  return [trimmed];
}
