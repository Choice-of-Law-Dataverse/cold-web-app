import { ref, computed } from "vue";
import type {
  FilterOption,
  FilterObjectOption,
  SearchFilters,
} from "@/types/api";
import type { LocationQuery } from "vue-router";

function isObjectOption(value: unknown): value is FilterObjectOption {
  return typeof value === "object" && value !== null && "label" in value;
}

export function useSearchFilters(initialFilters: LocationQuery = {}) {
  const currentJurisdictionFilter = ref<FilterOption[]>([]);
  const currentThemeFilter = ref<FilterOption[]>([]);
  const currentTypeFilter = ref<FilterOption[]>([]);
  const selectValue = ref(String(initialFilters.sortBy || "relevance"));

  const hasActiveFilters = computed(
    () =>
      currentJurisdictionFilter.value.length > 0 ||
      currentThemeFilter.value.length > 0 ||
      currentTypeFilter.value.length > 0,
  );

  const parseQueryParam = (param: string | undefined): string[] =>
    param ? param.split(",").filter(Boolean) : [];

  const buildFilterObject = (
    jurisdiction: FilterOption[],
    theme: FilterOption[],
    type: FilterOption[],
    sort: string,
  ): SearchFilters => ({
    jurisdiction:
      jurisdiction.length > 0
        ? jurisdiction
            .filter(
              (item) =>
                item !== "All Jurisdictions" &&
                (isObjectOption(item)
                  ? item.label !== "All Jurisdictions"
                  : true),
            )
            .map((item) => (isObjectOption(item) ? item.label : item))
            .join(",")
        : undefined,
    theme:
      theme.length > 0
        ? theme
            .map((item) => (isObjectOption(item) ? item.label : item))
            .join(",")
        : undefined,
    type:
      type.length > 0
        ? type
            .map((item) => (isObjectOption(item) ? item.label : item))
            .join(",")
        : undefined,
    sortBy: (sort || "relevance") as SearchFilters["sortBy"],
  });

  const resetFilters = () => {
    currentJurisdictionFilter.value = [];
    currentThemeFilter.value = [];
    currentTypeFilter.value = [];
  };

  const syncFiltersFromQuery = (query: LocationQuery) => {
    const { sortBy, jurisdiction, theme, type } = query;

    if (sortBy && String(sortBy) !== selectValue.value) {
      selectValue.value = String(sortBy);
    }

    const newJurisdiction = parseQueryParam(
      jurisdiction ? String(jurisdiction) : undefined,
    );
    const newTheme = parseQueryParam(theme ? String(theme) : undefined);
    const newType = parseQueryParam(type ? String(type) : undefined);

    if (
      JSON.stringify(newJurisdiction) !==
      JSON.stringify(currentJurisdictionFilter.value)
    ) {
      currentJurisdictionFilter.value = newJurisdiction;
    }
    if (JSON.stringify(newTheme) !== JSON.stringify(currentThemeFilter.value)) {
      currentThemeFilter.value = newTheme;
    }
    if (JSON.stringify(newType) !== JSON.stringify(currentTypeFilter.value)) {
      currentTypeFilter.value = newType;
    }
  };

  return {
    currentJurisdictionFilter,
    currentThemeFilter,
    currentTypeFilter,
    selectValue,
    hasActiveFilters,
    buildFilterObject,
    resetFilters,
    syncFiltersFromQuery,
  };
}
