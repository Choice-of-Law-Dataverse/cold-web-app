/**
 * Utility function to generate consistent page titles for CoLD application
 * @param titleParts - Array of title components (will be filtered for truthy, non-empty values)
 * @param fallback - Fallback title to use if no valid title parts are provided
 * @returns Formatted page title with "CoLD" suffix
 */
export function generatePageTitle(
  titleParts: (string | null | undefined)[],
  fallback: string,
): string {
  const validParts = titleParts
    .filter((part): part is string => Boolean(part?.trim()))
    .map((part) => part.trim());

  if (validParts.length > 0) {
    return [...validParts, fallback, "CoLD"].join(" — ");
  }

  return [fallback, "CoLD"].join(" — ");
}
