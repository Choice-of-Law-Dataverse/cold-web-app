<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <!-- Flexbox/Grid Container: Filters and Results Heading -->
        <div
          class="filters-header mb-6 flex flex-col md:flex-row md:justify-between md:items-center gap-4"
        >
          <!-- Left-aligned group of filters -->
          <div class="flex flex-col sm:flex-row gap-5 w-full">
            <SearchFilters
              :options="jurisdictionOptions"
              v-model="currentJurisdictionFilter"
              class="w-full sm:w-auto"
            />
            <SearchFilters
              :options="themeOptions"
              v-model="currentThemeFilter"
              class="w-full sm:w-auto"
            />
            <SearchFilters
              :options="typeOptions"
              v-model="currentTypeFilter"
              class="w-full sm:w-auto"
            />
            <UButton
              v-if="hasActiveFilters"
              variant="link"
              @click="resetFilters"
              class="w-full sm:w-auto link-button"
            >
              Reset
            </UButton>
          </div>

          <!-- Right-aligned Results Heading -->
          <h2
            class="text-right md:text-left w-full md:w-auto whitespace-nowrap"
          >
            {{ props.totalMatches }} Results
          </h2>
        </div>

        <!-- Results Grid or Messages -->
        <div class="results-content mt-4">
          <!-- Loading State -->
          <p v-if="loading">Loading…</p>

          <!-- No Results -->
          <NoSearchResults v-else-if="!allResults.length" />

          <!-- Results Grid -->
          <div v-else class="results-grid">
            <div
              v-for="(resultData, key) in allResults"
              :key="key"
              class="result-item"
            >
              <component
                :is="getResultComponent(resultData.source_table)"
                :resultData="resultData"
              />
            </div>
          </div>
          <div v-if="!loading" class="result-value-small text-center pt-4">
            <UButton
              to="/learn?tab=methodology#how-the-search-works"
              variant="link"
              icon="i-material-symbols:arrow-forward"
              trailing
              >Learn how the search works</UButton
            >
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

import ResultCard from './components/search-results/ResultCard.vue'
import LegislationCard from './components/search-results/LegislationCard.vue'
import LiteratureCard from './components/search-results/LiteratureCard.vue'
import CourtDecisionCard from './components/search-results/CourtDecisionCard.vue'
import AnswerCard from './components/search-results/AnswerCard.vue'
import SearchFilters from './components/search-results/SearchFilters.vue'
import NoSearchResults from './components/search-results/NoSearchResults.vue'

const getResultComponent = (source_table) => {
  switch (source_table) {
    case 'Domestic Instruments':
      return LegislationCard
    case 'Court Decisions':
      return CourtDecisionCard
    case 'Answers':
      return AnswerCard
    case 'Literature':
      return LiteratureCard
    default:
      return ResultCard
  }
}

// Props to receive current filter values
const props = defineProps({
  data: {
    type: Object,
    default: () => ({ tables: {} }), // Default to an object with an empty tables field
  },
  filters: {
    type: Object,
    required: true,
  },
  totalMatches: {
    type: Number,
    default: 0,
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

// Gather all results
const allResults = computed(() => {
  return Object.values(props.data?.tables || {}) // Fallback to an empty object
})

const emit = defineEmits(['update:filters'])

// Jurisdiction options state
const jurisdictionOptions = ref(['All Jurisdictions'])

// Fetch jurisdictions from file
const loadJurisdictions = async () => {
  try {
    const config = useRuntimeConfig() // Ensure config is accessible

    const jsonPayloads = [{ table: 'Jurisdictions', filters: [] }]

    // Fetch both tables concurrently
    const responses = await Promise.all(
      jsonPayloads.map((payload) =>
        fetch(`${config.public.apiBaseUrl}/search/full_table`, {
          method: 'POST',
          headers: {
            authorization: `Bearer ${config.public.FASTAPI}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        })
      )
    )

    // Process both responses
    const [jurisdictionsData, instrumentsData] = await Promise.all(
      responses.map((res) =>
        res.ok ? res.json() : Promise.reject('Failed to load data')
      )
    )

    // Filter out "Irrelevant?" only for "Jurisdictions"
    const relevantJurisdictions = jurisdictionsData.filter(
      (entry) => entry['Irrelevant?'] === null
    )

    // Extract "Name" fields
    const jurisdictionNames = relevantJurisdictions
      .map((entry) => entry.Name)
      .filter(Boolean)

    // Merge both lists, remove duplicates, and sort alphabetically
    const sortedJurisdictions = [
      ...new Set([...jurisdictionNames]), // ...instrumentNames]),
    ].sort((a, b) => a.localeCompare(b))

    // Prepend "All Jurisdictions" to the list
    jurisdictionOptions.value = ['All Jurisdictions', ...sortedJurisdictions]
  } catch (error) {
    console.error('Error loading jurisdictions:', error)
  }
}

// Call the function on mount
onMounted(() => {
  loadJurisdictions()
})

const themeOptions = [
  'All Themes',
  'Codification',
  'HCCH Principles',
  'Party autonomy',
  'Freedom of choice',
  'Dépeçage',
  'Partial choice',
  'Rules of law',
  'Tacit choice',
  'Overriding mandatory rules',
  'Public policy',
  'Absence of choice',
  'Arbitration',
]

const typeOptions = [
  'All Types',
  'Court Decisions',
  'Legal Instruments',
  'Literature',
  'Questions',
]

// Reactive states initialized from props
const currentJurisdictionFilter = ref(
  props.filters.theme || 'All Jurisdictions'
)
const currentThemeFilter = ref(props.filters.theme || 'All Themes')
const currentTypeFilter = ref(props.filters.type || 'All Types')

// Computed property to check if any filter is active
const hasActiveFilters = computed(() => {
  return (
    currentJurisdictionFilter.value !== 'All Jurisdictions' ||
    currentThemeFilter.value !== 'All Themes' ||
    currentTypeFilter.value !== 'All Types'
  )
})

// Function to reset all filters to their default states
const resetFilters = () => {
  currentJurisdictionFilter.value = 'All Jurisdictions'
  currentThemeFilter.value = 'All Themes'
  currentTypeFilter.value = 'All Types'
}

// Watch for changes in either filter and emit them up
watch(
  [currentJurisdictionFilter, currentThemeFilter, currentTypeFilter],
  ([newJurisdiction, newTheme, newType]) => {
    emit('update:filters', {
      jurisdiction: newJurisdiction,
      theme: newTheme,
      type: newType,
    })
  }
)

// Watch for prop changes to re-sync dropdowns when parent updates
watch(
  () => props.filters,
  (newFilters) => {
    currentJurisdictionFilter.value =
      newFilters.jurisdiction || 'All Jurisdictions'
    currentThemeFilter.value = newFilters.theme || 'All Themes'
    currentTypeFilter.value = newFilters.type || 'All Types'
  },
  { deep: true, immediate: true }
)
</script>

<style scoped>
.filters-header {
  display: flex;
  align-items: center; /* Vertically align items */
  justify-content: space-between; /* Space between SearchFilters and h2 */
  padding-bottom: 12px;
}

.filters-header h2 {
  margin: 0; /* Remove default margin for better alignment */
  padding-bottom: 0; /* Override inline padding if needed */
}
</style>
