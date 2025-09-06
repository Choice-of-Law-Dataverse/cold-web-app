import { ref, computed } from 'vue'

// Shared state for jurisdiction comparison filters
const currentJurisdictionFilter1 = ref([])
const currentJurisdictionFilter2 = ref([])
const currentJurisdictionFilter3 = ref([])
const jurisdictionOptions = ref([{ label: 'Loading…' }])
const loadingJurisdictions = ref(true)

export function useJurisdictionComparison() {
  // Create computed array for easier iteration
  const jurisdictionFilters = computed(() => [
    { value: currentJurisdictionFilter1 },
    { value: currentJurisdictionFilter2 },
    { value: currentJurisdictionFilter3 },
  ])

  // Computed property to get ISO3 codes from selected jurisdictions
  const selectedJurisdictionCodes = computed(() => {
    return jurisdictionFilters.value.map((filter) => {
      const selected = filter.value.value[0]
      return selected?.alpha3Code || null
    })
  })

  // Function to set initial filter values
  const setInitialFilters = (options, initialCountries = []) => {
    if (initialCountries.length === 3) {
      // Set filters based on URL country codes
      const filters = [
        currentJurisdictionFilter1,
        currentJurisdictionFilter2,
        currentJurisdictionFilter3,
      ]

      initialCountries.forEach((countryCode, index) => {
        const matchingCountry = options.find(
          (opt) =>
            opt.alpha3Code &&
            opt.alpha3Code.toUpperCase() === countryCode.toUpperCase()
        )
        if (matchingCountry && filters[index]) {
          filters[index].value = [matchingCountry]
        }
      })
    } else {
      // Set each filter to the first country (not 'Loading…') as default
      const firstCountry = options.find((opt) => opt.label !== 'Loading…')
      if (firstCountry) {
        currentJurisdictionFilter1.value = [firstCountry]
        currentJurisdictionFilter2.value = [firstCountry]
        currentJurisdictionFilter3.value = [firstCountry]
      }
    }
  }

  return {
    // State
    currentJurisdictionFilter1,
    currentJurisdictionFilter2,
    currentJurisdictionFilter3,
    jurisdictionOptions,
    loadingJurisdictions,

    // Computed
    jurisdictionFilters,
    selectedJurisdictionCodes,

    // Methods
    setInitialFilters,
  }
}
