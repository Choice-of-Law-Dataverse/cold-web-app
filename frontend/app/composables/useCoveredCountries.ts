import { computed } from "vue";
import { useJurisdictions } from "@/composables/useJurisdictions";

export function useCoveredCountries() {
  const { data: jurisdictions, ...rest } = useJurisdictions();

  const data = computed(() => {
    if (!jurisdictions.value) return undefined;

    return new Set(
      jurisdictions.value
        .filter(
          (jurisdiction) =>
            jurisdiction.answerCoverage &&
            jurisdiction.answerCoverage > 0 &&
            jurisdiction.alpha3Code,
        )
        .map((jurisdiction) => jurisdiction.alpha3Code!.toLowerCase()),
    );
  });

  return {
    data,
    ...rest,
  };
}
