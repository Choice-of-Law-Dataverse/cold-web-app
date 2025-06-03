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
          <span
            class="text-right md:text-left w-full md:w-auto whitespace-nowrap result-value-small flex items-center gap-2"
          >
            <span>{{ props.totalMatches }} results sorted by</span>
            <USelect
              color="primary"
              variant="none"
              :options="['relevance', 'date']"
              model-value="relevance"
              class="min-w-[120px] flex-shrink-0 truncate"
              style="color: var(--color-cold-purple)"
            />
          </span>
        </div>

        <!-- Results Grid or Messages -->
        <div class="results-content mt-4">
          <!-- Show loading skeleton only if loading and no results yet -->
          <div v-if="loading && !allResults.length">
            <LoadingCard />
          </div>

          <!-- No Results -->
          <NoSearchResults v-else-if="!loading && !allResults.length" />

          <!-- Results Grid: always show if there are results -->
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
            <!-- Show a loading spinner/card at the bottom if loading more -->
            <div v-if="loading && allResults.length" class="text-center py-4">
              <LoadingCard />
            </div>
          </div>

          <div
            v-if="props.canLoadMore && !loading"
            class="mt-16 mb-4 text-center"
          >
            <UButton
              native-type="button"
              @click.prevent="emit('load-more')"
              class="suggestion-button"
              variant="link"
              icon="i-material-symbols:arrow-cool-down"
              :disabled="props.loading"
            >
              Load More Results
            </UButton>
          </div>

          <div v-if="!loading" class="result-value-small text-center pt-4">
            <UButton
              to="https://choice-of-law-dataverse.github.io/search-algorithm"
              variant="link"
              target="_blank"
              >Learn How the Search Works</UButton
            >
            <UIcon
              name="i-material-symbols:play-arrow"
              class="inline-block ml-[-6px]"
              style="
                color: var(--color-cold-purple);
                position: relative;
                top: 2px;
              "
            />
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
import RegionalInstrumentCard from './components/search-results/RegionalInstrumentCard.vue'
import InternationalInstrumentCard from './components/search-results/InternationalInstrumentCard.vue'
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
    case 'Regional Instruments':
      return RegionalInstrumentCard
    case 'International Instruments':
      return InternationalInstrumentCard
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
      (a.label || '').localeCompare(b.label || '')
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
  'Domestic Instruments',
  'Regional Instruments',
  'International Instruments',
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

.result-value-small {
  font-weight: 600 !important;
}
</style>
