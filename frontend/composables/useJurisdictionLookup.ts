import { useJurisdictions } from "@/composables/useJurisdictions";

/**
 * Provides lookup utilities for jurisdictions using the API data.
 * Replaces the static jurisdictions-data.json with dynamic API data.
 * Leverages TanStack Query cache from useJurisdictions for efficient data access.
 */
export function useJurisdictionLookup() {
  const {
    data: jurisdictions,
    knownJurisdictionTerms,
    ...rest
  } = useJurisdictions();

  /**
   * Finds the ISO-3 code for a given jurisdiction name.
   * @param name - The jurisdiction name to look up
   * @returns The lowercase ISO-3 code, or "default" if not found
   */
  const getJurisdictionISO = (name: string): string => {
    if (!jurisdictions.value || !name) return "default";

    const jurisdiction = jurisdictions.value.find(
      (j) => j.Name.toLowerCase() === name.toLowerCase(),
    );

    return jurisdiction?.alpha3Code?.toLowerCase() || "default";
  };

  /**
   * Finds jurisdictions that match the given search words.
   * Searches in both the jurisdiction name and ISO-3 code.
   * @param words - Array of search words (lowercase)
   * @returns Array of matching jurisdiction names
   */
  const findMatchingJurisdictions = (words: string[]): string[] => {
    if (!jurisdictions.value || words.length === 0) return [];

    return jurisdictions.value
      .filter((j) =>
        words.some((word) => {
          const nameLower = j.Name.toLowerCase();
          const codeLower = j.alpha3Code?.toLowerCase() || "";
          return nameLower.includes(word) || codeLower.includes(word);
        }),
      )
      .map((j) => j.Name);
  };

  /**
   * Finds a jurisdiction by its exact name.
   * @param name - The jurisdiction name to find
   * @returns The jurisdiction object or undefined
   */
  const findJurisdictionByName = (name: string) => {
    if (!jurisdictions.value || !name) return undefined;

    return jurisdictions.value.find(
      (j) => j.Name.toLowerCase() === name.toLowerCase(),
    );
  };

  /**
   * Checks if a word matches any jurisdiction term.
   * @param word - The word to check (lowercase)
   * @returns true if the word matches a jurisdiction term
   */
  const isJurisdictionTerm = (word: string): boolean => {
    return knownJurisdictionTerms.value.has(word.toLowerCase());
  };

  return {
    ...rest,
    data: jurisdictions,
    knownJurisdictionTerms,
    getJurisdictionISO,
    findMatchingJurisdictions,
    findJurisdictionByName,
    isJurisdictionTerm,
  };
}
