import { ref, computed } from 'vue'

// Shared state for jurisdiction comparison filters
const currentJurisdictionFilter1 = ref([])
const currentJurisdictionFilter2 = ref([])
const currentJurisdictionFilter3 = ref([])
const showThirdColumn = ref(false)

export function useJurisdictionComparison() {
  // Create computed array for easier iteration
  const jurisdictionFilters = computed(() => {
    const base = [
      { value: currentJurisdictionFilter1 },
      { value: currentJurisdictionFilter2 },
    ]
    return showThirdColumn.value
      ? [...base, { value: currentJurisdictionFilter3 }]
      : base
  })

  // Computed property to get ISO3 codes from selected jurisdictions
  const selectedJurisdictionCodes = computed(() => {
    return jurisdictionFilters.value.map((filter) => {
      const selected = filter.value.value[0]
      return selected?.alpha3Code || null
    })
  })

  // Function to set initial filter values
  const setInitialFilters = (options, initialCountries = []) => {
    // Determine initial visibility of the third column
    showThirdColumn.value = initialCountries.length === 3

    const setFilterToCode = (targetRef, code) => {
      const match = options.find(
        (opt) => opt.alpha3Code && opt.alpha3Code.toUpperCase() === code
      )
      if (match) targetRef.value = [match]
    }

    if (initialCountries.length === 2 || initialCountries.length === 3) {
      const upper = initialCountries.map((c) => c.toUpperCase())
      setFilterToCode(currentJurisdictionFilter1, upper[0])
      setFilterToCode(currentJurisdictionFilter2, upper[1])
      if (upper[2]) setFilterToCode(currentJurisdictionFilter3, upper[2])
      if (!upper[2]) currentJurisdictionFilter3.value = []
    } else {
      // Default: initialize the first two filters; leave third empty
      const firstCountry = options.find((opt) => opt.label !== 'Loading…')
      if (firstCountry) {
        currentJurisdictionFilter1.value = [firstCountry]
        currentJurisdictionFilter2.value = [firstCountry]
      }
      currentJurisdictionFilter3.value = []
    }
  }

  return {
    // State
    currentJurisdictionFilter1,
    currentJurisdictionFilter2,
    currentJurisdictionFilter3,

    showThirdColumn,

    // Computed
    jurisdictionFilters,
    selectedJurisdictionCodes,

    // Methods
    setInitialFilters,
  }
}
