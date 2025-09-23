import { ref, computed } from 'vue'

export const useSearchFilters = (initialFilters = {}) => {
  const currentJurisdictionFilter = ref([])
  const currentThemeFilter = ref([])
  const currentTypeFilter = ref([])
  const selectValue = ref(initialFilters.sortBy || 'relevance')

  const hasActiveFilters = computed(
    () =>
      currentJurisdictionFilter.value.length > 0 ||
      currentThemeFilter.value.length > 0 ||
      currentTypeFilter.value.length > 0
  )

  const parseQueryParam = (param) =>
    param ? param.split(',').filter(Boolean) : []

  const buildFilterObject = (jurisdiction, theme, type, sort) => ({
    jurisdiction:
      jurisdiction.length > 0
        ? jurisdiction
            .filter(
              (item) =>
                item !== 'All Jurisdictions' &&
                item.label !== 'All Jurisdictions'
            )
            .map((item) => item?.label || item)
            .join(',')
        : undefined,
    theme: theme.length > 0 ? theme.join(',') : undefined,
    type: type.length > 0 ? type.join(',') : undefined,
    sortBy: sort || 'relevance',
  })

  const resetFilters = () => {
    currentJurisdictionFilter.value = []
    currentThemeFilter.value = []
    currentTypeFilter.value = []
  }

  const syncFiltersFromQuery = (query) => {
    const { sortBy, jurisdiction, theme, type } = query

    if (sortBy && sortBy !== selectValue.value) {
      selectValue.value = sortBy
    }

    const newJurisdiction = parseQueryParam(jurisdiction)
    const newTheme = parseQueryParam(theme)
    const newType = parseQueryParam(type)

    if (
      JSON.stringify(newJurisdiction) !==
      JSON.stringify(currentJurisdictionFilter.value)
    ) {
      currentJurisdictionFilter.value = newJurisdiction
    }
    if (JSON.stringify(newTheme) !== JSON.stringify(currentThemeFilter.value)) {
      currentThemeFilter.value = newTheme
    }
    if (JSON.stringify(newType) !== JSON.stringify(currentTypeFilter.value)) {
      currentTypeFilter.value = newType
    }
  }

  return {
    currentJurisdictionFilter,
    currentThemeFilter,
    currentTypeFilter,
    selectValue,
    hasActiveFilters,
    buildFilterObject,
    resetFilters,
    syncFiltersFromQuery,
  }
}
