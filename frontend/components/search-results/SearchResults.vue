<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <!-- Flexbox/Grid Container: Filters and Results Heading -->
        <div
          class="filters-header mb-6 ml-[-1px] flex flex-col md:flex-row md:justify-between md:items-center gap-4"
        >
          <!-- Left-aligned group of filters -->
          <div class="flex flex-col sm:flex-row gap-5 w-full">
            <SearchFilters
              :options="jurisdictionOptions"
              v-model="currentJurisdictionFilter"
              class="w-full sm:w-auto"
              showAvatars="true"
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
          <p v-if="loading">
            <LoadingCard />
          </p>

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
              to="/learn/methodology#How-the-Search-Works"
              variant="link"
              icon="i-material-symbols:arrow-forward"
              trailing
              >Learn how the search works</UButton
            >
          </div>
          <div v-if="props.canLoadMore" class="mt-4 text-center">
            <UButton
              native-type="button"
              @click.prevent="emit('load-more')"
              class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
              :disabled="props.loading"
            >
              {{ props.loading ? 'Loading...' : 'Load more results' }}
            </UButton>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue'

import ResultCard from './components/search-results/ResultCard.vue'
import LegislationCard from './components/search-results/LegislationCard.vue'
import LiteratureCard from './components/search-results/LiteratureCard.vue'
import CourtDecisionCard from './components/search-results/CourtDecisionCard.vue'
import AnswerCard from './components/search-results/AnswerCard.vue'
import SearchFilters from './components/search-results/SearchFilters.vue'
import NoSearchResults from './components/search-results/NoSearchResults.vue'
import LoadingCard from './components/layout/LoadingCard.vue'

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
  canLoadMore: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:filters', 'load-more'])

// Gather all results
const allResults = computed(() => {
  return Object.values(props.data?.tables || {}) // Fallback to an empty object
})

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

    // Filter out "Irrelevant?" for "Jurisdictions"
    const relevantJurisdictions = jurisdictionsData.filter(
      (entry) => entry['Irrelevant?'] === null
    )

    // Map each entry to an object with label and avatar
    const mappedJurisdictions = relevantJurisdictions.map((entry) => ({
      label: entry.Name,
      avatar: entry['Alpha-3 Code']
        ? `https://choiceoflawdataverse.blob.core.windows.net/assets/flags/${entry['Alpha-3 Code'].toLowerCase()}.svg`
        : undefined,
    }))

    // Sort alphabetically by label
    const sortedJurisdictions = mappedJurisdictions.sort((a, b) =>
      a.label.localeCompare(b.label)
    )

    // Prepend "All Jurisdictions" to the list
    jurisdictionOptions.value = [
      { label: 'All Jurisdictions' },
      ...sortedJurisdictions,
    ]
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
const currentJurisdictionFilter = ref([])
const currentThemeFilter = ref([])
const currentTypeFilter = ref([])

// Computed property to check if any filter is active
const hasActiveFilters = computed(() => {
  return (
    currentJurisdictionFilter.value.length > 0 ||
    currentThemeFilter.value.length > 0 ||
    currentTypeFilter.value.length > 0
  )
})

// Function to reset all filters to their default states
const resetFilters = () => {
  currentJurisdictionFilter.value = []
  currentThemeFilter.value = []
  currentTypeFilter.value = []
}

// Watch for changes in either filter and emit them up
watch(
  [currentJurisdictionFilter, currentThemeFilter, currentTypeFilter],
  ([newJurisdiction, newTheme, newType]) => {
    const filters = {
      jurisdiction:
        newJurisdiction.length > 0
          ? newJurisdiction
              .map((item) => (typeof item === 'object' ? item.label : item))
              .join(',')
          : undefined,
      theme: newTheme.length > 0 ? newTheme.join(',') : undefined,
      type: newType.length > 0 ? newType.join(',') : undefined,
    }

    // Only emit if filters have changed
    if (JSON.stringify(filters) !== JSON.stringify(props.filters)) {
      emit('update:filters', filters)
    }
  },
  { deep: true }
)

// Watch for prop changes to re-sync dropdowns when parent updates
watch(
  () => props.filters,
  (newFilters) => {
    // Convert filter strings to arrays, handling both single and multiple selections
    const newJurisdiction = newFilters.jurisdiction
      ? newFilters.jurisdiction.split(',').filter(Boolean)
      : []
    const newTheme = newFilters.theme
      ? newFilters.theme.split(',').filter(Boolean)
      : []
    const newType = newFilters.type
      ? newFilters.type.split(',').filter(Boolean)
      : []

    // Only update if the values have actually changed
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
  },
  { deep: true, immediate: true } // Add immediate to handle initial props
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
