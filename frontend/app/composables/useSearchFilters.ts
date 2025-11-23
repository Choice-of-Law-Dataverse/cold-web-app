import { ref, computed } from "vue";
import type { SearchFilters } from "@/types/api";

/**
 * Composable for managing search filters
 * Returns refs that components can v-model to
 */
export const useSearchFilters = () => {
  // Simple refs - no computed, no router calls
  const currentJurisdictionFilter = ref<string[]>([]);
  const currentThemeFilter = ref<string[]>([]);
  const currentTypeFilter = ref<string[]>([]);
  const selectValue = ref<"date" | "relevance">("relevance");

  // Check if any filters are active
  const hasActiveFilters = computed(
    () =>
      currentJurisdictionFilter.value.length > 0 ||
      currentThemeFilter.value.length > 0 ||
      currentTypeFilter.value.length > 0,
  );

  // Build filter object for API requests
  const buildFilterObject = computed((): SearchFilters => {
    const filters: SearchFilters = {
      sortBy: selectValue.value,
    };

    const jurisdiction = currentJurisdictionFilter.value
      .filter((item) => item !== "All Jurisdictions" && item !== "all")
      .join(",");

    if (jurisdiction) {
      filters.jurisdiction = jurisdiction;
    }

    const theme = currentThemeFilter.value.join(",");
    if (theme) {
      filters.theme = theme;
    }

    const type = currentTypeFilter.value.join(",");
    if (type) {
      filters.type = type;
    }

    return filters;
  });

  // Reset filters
  const resetFilters = () => {
    currentJurisdictionFilter.value = [];
    currentThemeFilter.value = [];
    currentTypeFilter.value = [];
  };

  return {
    // Reactive filter refs (can be v-modeled)
    currentJurisdictionFilter,
    currentThemeFilter,
    currentTypeFilter,
    selectValue,

    // Computed states
    hasActiveFilters,
    filters: buildFilterObject,

    // Actions
    resetFilters,
  };
};
