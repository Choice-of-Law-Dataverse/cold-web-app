import { useQuery } from "@tanstack/vue-query";

const fetchCoveredCountries = async (): Promise<Set<string>> => {
  const response = await fetch("/temp_answer_coverage.txt");
  if (!response.ok) {
    throw new Error("Failed to fetch countries file");
  }
  const text = await response.text();
  const countries = text
    .split("\n")
    .map((line) => line.trim().toLowerCase()) // Convert to lowercase for consistent comparison
    .filter((line) => line.length > 0); // Filter out empty lines

  return new Set(countries);
};

export function useCoveredCountries() {
  return useQuery({
    queryKey: ["coveredCountries"],
    queryFn: fetchCoveredCountries,
  });
}
