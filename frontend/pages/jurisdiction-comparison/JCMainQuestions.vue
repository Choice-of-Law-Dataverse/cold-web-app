<template>
  <div>
    <!-- Desktop Layout -->
    <div class="hidden md:block">
      <div class="jc-grid jc-overview-row">
        <div class="jc-col-1">
          <h2 class="mt-8 mb-6 mr-[106px]">Main Questions</h2>
        </div>
      </div>
      <hr class="jc-hr" />
      <div class="jc-table-grid">
        <div
          v-for="(label, i) in questionLabels"
          :key="'q-row-' + i"
          class="jc-table-row"
        >
          <div class="jc-table-cell jc-table-question">
            {{ label }}
          </div>
          <div
            class="jc-table-cell jc-table-answer"
            v-for="j in 3"
            :key="'a-' + i + '-' + j"
          >
            {{ sampleData[i] }}
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile & Tablet Layout -->
    <div class="md:hidden">
      <div class="mobile-layout">
        <!-- Header -->
        <div class="mb-6">
          <h2 class="text-xl font-semibold">Select Jurisdictions</h2>
        </div>

        <!-- Filters in a responsive grid -->
        <div class="filters-grid mb-6">
          <div
            v-for="(filter, index) in jurisdictionFilters"
            :key="`mobile-filter-${index}`"
            class="filter-item"
          >
            <label class="block text-sm font-medium mb-2 text-gray-700">
              <!-- Jurisdiction {{ index + 1 }} -->
            </label>
            <SearchFilters
              :options="jurisdictionOptions"
              v-model="filter.value.value"
              class="w-full"
              showAvatars="true"
              :multiple="false"
            />
          </div>
        </div>

        <hr class="border-gray-300 mb-6" />

        <!-- Data cards -->
        <div class="data-cards">
          <h2 class="mt-4">Overview</h2>
          <div class="data-card grid grid-cols-4 gap-0">
            <div class="data-card-labels flex flex-col">
              <p
                v-for="(label, i) in questionLabels"
                :key="'q-label-m-' + i"
                class="data-line"
              >
                {{ label }}
              </p>
            </div>
            <div
              v-for="(filter, index) in jurisdictionFilters"
              :key="`mobile-data-${index}`"
              class="data-card flex flex-col"
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
              <div class="data-card-content">
                <p
                  v-for="(line, lineIndex) in sampleData"
                  :key="'m-' + lineIndex"
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import SearchFilters from '@/components/search-results/SearchFilters.vue'

// Initialize jurisdiction options with default value
const jurisdictionOptions = ref([{ label: 'All Jurisdictions' }])

// Create reactive filter references
const currentJurisdictionFilter1 = ref([])
const currentJurisdictionFilter2 = ref([])
const currentJurisdictionFilter3 = ref([])

// Create computed array for easier iteration
const jurisdictionFilters = computed(() => [
  { value: currentJurisdictionFilter1 },
  { value: currentJurisdictionFilter2 },
  { value: currentJurisdictionFilter3 },
])

// Static sample data as computed property
const questionLabels = [
  'Is the principle of party autonomy in respect of choice of law in international commercial contracts widely accepted in this jurisdiction?',
  'Is a connection required between the chosen law and the parties or their transaction? ',
  'Are the parties prevented from choosing the law of a third country with which there is no connection (a “neutral law”)?',
  'Are the parties allowed to choose non-State law (“rules of law”) to govern their contract?',
]
const sampleData = computed(() => ['Yes', 'No', 'Yes', 'No'])

// Data fetching
const loadJurisdictions = async () => {
  try {
    const config = useRuntimeConfig()
    const response = await fetch(
      `${config.public.apiBaseUrl}/search/full_table`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ table: 'Jurisdictions', filters: [] }),
      }
    )

    if (!response.ok) throw new Error('Failed to load jurisdictions')

    const jurisdictionsData = await response.json()
    jurisdictionOptions.value = [
      { label: 'All Jurisdictions' },
      ...jurisdictionsData
        .filter((entry) => entry['Irrelevant?'] === null)
        .map((entry) => ({
          label: entry.Name,
          avatar: entry['Alpha-3 Code']
            ? `https://choiceoflawdataverse.blob.core.windows.net/assets/flags/${entry['Alpha-3 Code'].toLowerCase()}.svg`
            : undefined,
        }))
        .sort((a, b) => (a.label || '').localeCompare(b.label || '')),
    ]
  } catch (error) {
    console.error('Error loading jurisdictions:', error)
  }
}

// Initialization
onMounted(async () => {
  await loadJurisdictions()
})
</script>

<style scoped>
/* Desktop Grid Layout */
.jc-grid {
  display: grid;
  grid-template-columns: 0.75fr 1fr 1fr 1fr;
  align-items: start;
  gap: 0 1.5rem;
}

.jc-overview-row {
  margin-bottom: 0;
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

@media (min-width: 640px) {
  .filters-grid {
    grid-template-columns: repeat(2, 1fr);
  }
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

@media (min-width: 640px) {
  .data-cards {
    grid-template-columns: repeat(2, 1fr);
  }
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
  color: #374151;
  line-height: 2;
}

.jc-hr {
  border-top: 1px solid var(--color-cold-gray);
}

.result-value-medium {
  font-weight: 400 !important;
  margin-top: 32px !important;
}

/* Search filter styling */
.jc-search-filter :deep(.cold-uselectmenu) {
  width: 270px !important;
}

/* Table-like grid for desktop */
.jc-table-grid {
  display: grid;
  grid-template-columns: 0.75fr 1fr 1fr 1fr;
  width: 100%;
}
.jc-table-row {
  display: contents;
}
.jc-table-cell {
  padding: 0.75rem 1rem 0.75rem 0;
  border-bottom: 1px solid var(--color-cold-gray);
  vertical-align: top;
  font-size: 1rem;
}
.jc-table-question {
  font-weight: 400;
  white-space: pre-line;
}
.jc-table-answer {
  text-align: left;
  font-weight: 400;
}
.jc-table-question-header {
  font-weight: 600;
  font-size: 1.1rem;
  border-bottom: none;
}
.jc-table-answer-header {
  font-weight: 600;
  font-size: 1.1rem;
  border-bottom: none;
}
</style>
