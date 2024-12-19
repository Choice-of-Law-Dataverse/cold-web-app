<template>
  <div class="container">
    <div class="col-span-12">
      <!-- Flexbox Container -->
      <div class="filters-header mb-6">
        <!-- Jurisdictions Filter -->
        <SearchFilters
          :options="jurisdictionOptions"
          v-model="currentJurisdictionFilter"
        />

        <!-- Themes Filter -->
        <SearchFilters :options="themeOptions" v-model="currentThemeFilter" />

        <!-- Types Filter -->
        <SearchFilters :options="typeOptions" v-model="currentTypeFilter" />

        <h2 class="text-right">{{ props.totalMatches }} Results</h2>
      </div>

      <!-- Results Grid -->
      <div class="results-grid">
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import LegislationCard from '@/components/LegislationCard.vue'
import CourtDecisionCard from '@/components/CourtDecisionCard.vue'
import AnswerCard from '@/components/AnswerCard.vue'
import ResultCard from '@/components/ResultCard.vue'
import SearchFilters from './SearchFilters.vue'

const getResultComponent = (source_table) => {
  switch (source_table) {
    case 'Legislation':
      return LegislationCard
    case 'Court decisions':
      return CourtDecisionCard
    case 'Answers':
      return AnswerCard
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
  'Express and tacit choice',
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
