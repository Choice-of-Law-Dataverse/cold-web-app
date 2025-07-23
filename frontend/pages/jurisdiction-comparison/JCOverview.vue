<template>
  <div>
    <div class="hidden md:block">
      <div class="mt-24 jc-z-top"></div>
      <hr class="jc-hr" />
      <div class="jc-grid jc-data-row">
        <div class="jc-col-1 jc-empty"></div>
        <div
          v-for="index in 3"
          :key="`desktop-data-${index}`"
          :class="`jc-col-${index + 1}`"
        >
          <div class="result-value-medium">
            <p
              v-for="(line, lineIndex) in getSampleDataForColumn(index - 1)"
              :key="lineIndex"
              class="pt-8"
            >
              {{ line }}
              <br
                v-if="lineIndex < getSampleDataForColumn(index - 1).length - 1"
              />
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile & Tablet Layout -->
    <div class="md:hidden">
      <div class="mobile-layout">
        <!-- Data cards -->
        <div class="data-cards">
          <h2 class="mt-4">Overview</h2>
          <div
            v-for="(filter, index) in jurisdictionFilters"
            :key="`mobile-data-${index}`"
            class="data-card"
          >
            <h3 class="data-card-title flex items-center">
              <template
                v-if="
                  filter.value.value.length > 0 &&
                  filter.value.value[0]?.label !== 'All Jurisdictions'
                "
              >
                <img
                  v-if="
                    !erroredFlags[index] &&
                    getFlagUrl(filter.value.value[0].label)
                  "
                  :src="getFlagUrl(filter.value.value[0].label)"
                  @error="() => (erroredFlags[index] = true)"
                  style="
                    height: 18px;
                    width: auto;
                    margin-right: 0.5em;
                    border-radius: 0;
                    border: 1px solid var(--color-cold-gray);
                  "
                  :alt="filter.value.value[0].label + ' flag'"
                />
                {{ filter.value.value[0].label }}
              </template>
              <template v-else>
                {{ `Jurisdiction ${index + 1}` }}
              </template>
            </h3>
            <div>
              <p
                v-for="(line, lineIndex) in getSampleDataForColumn(index)"
                :key="lineIndex"
                class="data-line"
              >
                {{ line }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useJurisdictionComparison } from '@/composables/useJurisdictionComparison'

// Use shared jurisdiction comparison state
const {
  jurisdictionOptions,
  jurisdictionFilters,
  selectedJurisdictionCodes,
  loadJurisdictions,
} = useJurisdictionComparison()

// Reactive state for legal families
const legalFamilies = ref({})
const loadingLegalFamily = ref({})

// Reactive state for court decisions count
const courtDecisionsCounts = ref({})
const loadingCourtDecisions = ref({})

// Reactive state for domestic instruments count
const domesticInstrumentsCounts = ref({})
const loadingDomesticInstruments = ref({})

// Function to fetch legal family for a jurisdiction
const fetchLegalFamily = async (iso3Code) => {
  if (!iso3Code || legalFamilies.value[iso3Code]) return

  loadingLegalFamily.value[iso3Code] = true

  try {
    const config = useRuntimeConfig()
    const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        authorization: `Bearer ${config.public.FASTAPI}`,
      },
      body: JSON.stringify({
        table: 'Jurisdictions',
        id: iso3Code,
      }),
    })

    if (response.ok) {
      const data = await response.json()
      legalFamilies.value[iso3Code] = data['Legal Family'] || 'Unknown'
    } else {
      legalFamilies.value[iso3Code] = 'Unknown'
    }
  } catch (error) {
    console.error(`Error fetching legal family for ${iso3Code}:`, error)
    legalFamilies.value[iso3Code] = 'Unknown'
  } finally {
    loadingLegalFamily.value[iso3Code] = false
  }
}

// Generic function to fetch data count for a jurisdiction by table type
const fetchDataCount = async (jurisdictionName, tableType) => {
  const countsRef =
    tableType === 'Court Decisions'
      ? courtDecisionsCounts
      : domesticInstrumentsCounts
  const loadingRef =
    tableType === 'Court Decisions'
      ? loadingCourtDecisions
      : loadingDomesticInstruments

  if (!jurisdictionName || countsRef.value[jurisdictionName]) return

  loadingRef.value[jurisdictionName] = true

  try {
    const config = useRuntimeConfig()
    const response = await fetch(`${config.public.apiBaseUrl}/search/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        authorization: `Bearer ${config.public.FASTAPI}`,
      },
      body: JSON.stringify({
        search_string: '',
        filters: [
          {
            column: 'tables',
            values: [tableType],
          },
          {
            column: 'jurisdictions',
            values: [jurisdictionName],
          },
        ],
      }),
    })

    if (response.ok) {
      const data = await response.json()
      countsRef.value[jurisdictionName] = data.total_matches || 0
    } else {
      countsRef.value[jurisdictionName] = 0
    }
  } catch (error) {
    console.error(
      `Error fetching ${tableType.toLowerCase()} for ${jurisdictionName}:`,
      error
    )
    countsRef.value[jurisdictionName] = 0
  } finally {
    loadingRef.value[jurisdictionName] = false
  }
}

// Wrapper functions for specific data types
const fetchCourtDecisions = (jurisdictionName) =>
  fetchDataCount(jurisdictionName, 'Court Decisions')
const fetchDomesticInstruments = (jurisdictionName) =>
  fetchDataCount(jurisdictionName, 'Domestic Instruments')

// Dynamic sample data based on selected jurisdictions
const getSampleDataForColumn = (columnIndex) => {
  const codes = selectedJurisdictionCodes.value
  const iso3Code = codes[columnIndex]

  // Get jurisdiction name from filters
  const filter = jurisdictionFilters.value[columnIndex]
  const jurisdictionName = filter?.value?.value?.[0]?.label

  // Fetch legal family if we have an ISO3 code
  if (
    iso3Code &&
    !legalFamilies.value[iso3Code] &&
    !loadingLegalFamily.value[iso3Code]
  ) {
    fetchLegalFamily(iso3Code)
  }

  // Fetch court decisions if we have a jurisdiction name
  if (
    jurisdictionName &&
    jurisdictionName !== 'All Jurisdictions' &&
    !courtDecisionsCounts.value[jurisdictionName] &&
    !loadingCourtDecisions.value[jurisdictionName]
  ) {
    fetchCourtDecisions(jurisdictionName)
  }

  // Fetch domestic instruments if we have a jurisdiction name
  if (
    jurisdictionName &&
    jurisdictionName !== 'All Jurisdictions' &&
    !domesticInstrumentsCounts.value[jurisdictionName] &&
    !loadingDomesticInstruments.value[jurisdictionName]
  ) {
    fetchDomesticInstruments(jurisdictionName)
  }

  const legalFamily = iso3Code
    ? legalFamilies.value[iso3Code] ||
      (loadingLegalFamily.value[iso3Code] ? 'Loading…' : 'Loading…')
    : 'Loading…'

  const courtDecisionsCount =
    jurisdictionName && jurisdictionName !== 'All Jurisdictions'
      ? courtDecisionsCounts.value[jurisdictionName] !== undefined
        ? `${courtDecisionsCounts.value[jurisdictionName]} court decisions`
        : loadingCourtDecisions.value[jurisdictionName]
          ? 'Loading…'
          : 'Loading…'
      : 'Loading…'

  const domesticInstrumentsCount =
    jurisdictionName && jurisdictionName !== 'All Jurisdictions'
      ? domesticInstrumentsCounts.value[jurisdictionName] !== undefined
        ? `${domesticInstrumentsCounts.value[jurisdictionName]} domestic instrument${domesticInstrumentsCounts.value[jurisdictionName] === 1 ? '' : 's'}`
        : loadingDomesticInstruments.value[jurisdictionName]
          ? 'Loading…'
          : 'Loading…'
      : 'Loading…'

  return [
    legalFamily,
    courtDecisionsCount,
    domesticInstrumentsCount,
    // '0 arbitration laws', // To Do: Add arbitration laws
  ]
}

// Watch for changes in selected jurisdiction codes to fetch legal families
watch(
  selectedJurisdictionCodes,
  (newCodes, oldCodes) => {
    newCodes.forEach((code, index) => {
      if (code && code !== oldCodes?.[index]) {
        fetchLegalFamily(code)
      }
    })
  },
  { immediate: true }
)

// Watch for changes in jurisdiction filters to fetch court decisions
watch(
  jurisdictionFilters,
  (newFilters, oldFilters) => {
    newFilters.forEach((filter, index) => {
      const jurisdictionName = filter?.value?.value?.[0]?.label
      const oldJurisdictionName = oldFilters?.[index]?.value?.value?.[0]?.label

      if (
        jurisdictionName &&
        jurisdictionName !== 'All Jurisdictions' &&
        jurisdictionName !== oldJurisdictionName
      ) {
        fetchCourtDecisions(jurisdictionName)
        fetchDomesticInstruments(jurisdictionName)
      }
    })
  },
  { immediate: true, deep: true }
)

// --- Flag logic ---
import { reactive } from 'vue'
const erroredFlags = reactive({})
function getFlagUrl(label) {
  if (!label || label === 'All Jurisdictions') return ''
  // Use Alpha-3 code if available in jurisdictionOptions
  const found = jurisdictionOptions.value.find((j) => j.label === label)
  if (found && found.avatar) return found.avatar
  // Fallback: try to use label as ISO code (lowercase)
  return `https://choiceoflawdataverse.blob.core.windows.net/assets/flags/${label.toLowerCase()}.svg`
}

// Initialization
onMounted(async () => {
  await loadJurisdictions()
})
</script>

<style scoped>
/* Desktop Grid Layout */

.jc-grid,
.jc-data-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  align-items: start;
  gap: 0 1.5rem;
}

.jc-overview-row {
  margin-bottom: 0;
  position: sticky;
  top: 0;
  background: #fff;
}

.jc-data-row {
  margin-top: 0;
}

.jc-col-1 {
  grid-column: 1;
}
.jc-col-2 {
  grid-column: 2;
}
.jc-col-3 {
  grid-column: 3;
}
.jc-col-4 {
  grid-column: 4;
}

/* Shared scrollbar styles */
.jc-mobile-filters-container,
.jc-mobile-data-container {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  padding: 1rem 0;
  scrollbar-width: thin;
  scrollbar-color: var(--color-cold-gray) transparent;
}

.jc-mobile-filters-container::-webkit-scrollbar,
.jc-mobile-data-container::-webkit-scrollbar {
  height: 6px;
}

/* Mobile & Tablet Layout */
.mobile-layout {
  padding: 0.25rem;
}

/* Filters grid for mobile */
.filters-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .filters-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.filter-item {
  display: flex;
  flex-direction: column;
}

/* Data cards for mobile */
.data-cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .data-cards {
    grid-template-columns: repeat(3, 1fr);
  }
}

.data-card {
  padding-top: 2rem;
}

.data-card-title {
  font-weight: 600;
  font-size: 1.125rem;
  margin-bottom: 1rem;
  color: var(--color-cold-purple);
}

.data-line {
  margin-bottom: 0.5rem;
  line-height: 2;
}

.result-value-medium {
  font-weight: 400 !important;
  margin-top: 32px !important;
}

/* Search filter styling */
.jc-search-filter {
  width: 240px;
  max-width: 100%;
}
.jc-search-filter :deep(.cold-uselectmenu) {
  width: 240px !important;
  min-width: 0 !important;
  max-width: 240px !important;
}

/* Highest z-index for Overview heading */
.jc-z-top {
  position: relative;
  pointer-events: none;
}
</style>
