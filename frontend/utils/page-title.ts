/**
 * Utility function to generate consistent page titles for CoLD application
 * @param titleParts - Array of title components (will be filtered for truthy, non-empty values)
 * @param fallback - Fallback title to use if no valid title parts are provided
 * @returns Formatted page title with "CoLD" suffix
 */
export function generatePageTitle(titleParts: (string | null | undefined)[], fallback: string): string {
  // Filter out null/undefined/empty values and trim whitespace
  const validParts = titleParts
    .filter((part): part is string => Boolean(part?.trim()))
    .map(part => part.trim());

  // If we have valid parts, join them with the fallback and "CoLD"
  if (validParts.length > 0) {
    return [...validParts, fallback, "CoLD"].join(" — ");
  }

  // Otherwise use just the fallback and "CoLD"
  return [fallback, "CoLD"].join(" — ");
}