<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <!-- Flexbox/Grid Container: Filters and Results Heading -->
        <div
          class="filters-header mb-6 flex flex-col md:flex-row md:justify-between md:items-center gap-4"
        >
          <!-- Left-aligned group of filters -->
          <div class="flex flex-col sm:flex-row gap-4 w-full">
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
              to="/learn?tab=how-search-works"
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

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import ResultCard from '@/components/ResultCard.vue'
import LegislationCard from '@/components/LegislationCard.vue'
import LiteratureCard from '@/components/LiteratureCard.vue'
import CourtDecisionCard from '@/components/CourtDecisionCard.vue'
import AnswerCard from '@/components/AnswerCard.vue'
import SearchFilters from './SearchFilters.vue'

const getResultComponent = (source_table) => {
  switch (source_table) {
    case 'Legislation':
      return LegislationCard
    case 'Court decisions':
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
    const response = await fetch('/temp_jurisdictions.txt') // File path in public/
    if (!response.ok) throw new Error('Failed to load jurisdictions')

    const text = await response.text()
    const jurisdictions = text
      .split('\n') // Split text into lines
      .map((line) => line.trim()) // Trim spaces
      .filter((line) => line) // Remove empty lines

    // Prepend "All Jurisdictions" to the list
    jurisdictionOptions.value = ['All Jurisdictions', ...jurisdictions]
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
  'Absence of choice',
  'Preamble',
  'Party autonomy',
  'Freedom of choice',
  'Partial choice',
  'Dépeçage',
  'Rules of law',
  'Tacit choice',
  'Mandatory rules',
  'Public policy',
  'Arbitration',
  'Scope of the Principles',
  'Formal validity of the choice of law',
  'Agreement on the choice of law and battle of forms',
  'Severability',
  'Exclusion of renvoi',
  'Scope of the chosen law',
  'Assignment',
  'Establishment',
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
