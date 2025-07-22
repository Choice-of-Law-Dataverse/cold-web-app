<template>
  <div>
    <!-- Desktop Layout -->
    <div class="hidden md:block">
      <div class="jc-grid jc-overview-row">
        <div class="jc-col-1 flex items-center">
          <button
            v-if="showCaret"
            @click="isOpen = !isOpen"
            class="accordion-caret mr-2 mt-2"
            style="
              background: none;
              border: none;
              padding: 0;
              cursor: pointer;
              display: flex;
              align-items: center;
            "
          >
            <svg
              :style="{
                transform: isOpen ? 'rotate(90deg)' : 'rotate(0deg)',
              }"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              width="16"
              height="16"
              fill="none"
              style="color: var(--color-cold-purple)"
            >
              <path
                d="M9 6l6 6-6 6"
                stroke="currentColor"
                stroke-width="3"
                stroke-linecap="square"
                stroke-linejoin="square"
              />
            </svg>
          </button>
          <h2 class="mt-8 mb-6 mr-[106px]">{{ props.title }}</h2>
        </div>
      </div>
      <hr class="jc-hr" />
      <div v-show="isOpen">
        <div v-if="loadingQuestions" class="flex justify-left py-8">
          <LoadingBar />
        </div>
        <div v-else class="jc-table-grid">
          <div
            v-for="(label, i) in questionLabels"
            :key="'q-row-' + i"
            class="jc-table-row"
          >
            <div class="jc-table-cell jc-table-question result-value-medium">
              {{ label }}
            </div>
            <div
              class="jc-table-cell jc-table-answer result-value-large !pt-10 !pl-2"
              v-for="j in 3"
              :key="'a-' + i + '-' + j"
            >
              {{ sampleData[i] }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile & Tablet Layout -->
    <div class="md:hidden">
      <div class="mobile-layout">
        <hr class="jc-hr mt-4 mb-12" />
        <div class="flex items-center mb-2 mt-4">
          <button
            v-if="showCaret"
            @click="isOpenMobile = !isOpenMobile"
            class="accordion-caret mr-2"
            style="
              background: none;
              border: none;
              padding: 0;
              cursor: pointer;
              display: flex;
              align-items: center;
            "
          >
            <svg
              :style="{
                transform: isOpenMobile ? 'rotate(90deg)' : 'rotate(0deg)',
              }"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              width="16"
              height="16"
              fill="none"
              style="color: var(--color-cold-purple)"
            >
              <path
                d="M9 6l6 6-6 6"
                stroke="currentColor"
                stroke-width="3"
                stroke-linecap="square"
                stroke-linejoin="square"
              />
            </svg>
          </button>
          <h2 class="mt-0">{{ props.title }}</h2>
        </div>
        <div v-show="isOpenMobile" class="data-cards">
          <div v-if="loadingQuestions" class="flex justify-left py-8">
            <LoadingBar />
          </div>
          <div v-else>
            <div
              v-for="(label, i) in questionLabels"
              :key="'q-label-m-' + i"
              class="mb-8"
            >
              <p class="data-line font-semibold mb-2">{{ label }}</p>
              <div
                v-for="(filter, index) in jurisdictionFilters"
                :key="`mobile-q-${i}-j-${index}`"
                class="mb-4"
              >
                <h3 class="data-card-title flex items-center mb-1">
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
                <div class="data-card-content result-value-large">
                  <p class="data-line">{{ sampleData[i] }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import LoadingBar from '@/components/layout/LoadingBar.vue'
const props = defineProps({
  showCaret: {
    type: Boolean,
    default: true,
  },
  title: {
    type: String,
    default: 'Please Set Title',
  },
})

// Accordion state
const isOpen = ref(false)
const isOpenMobile = ref(false)

// Always force open if showCaret is false
watch(
  () => props.showCaret,
  (val) => {
    if (!val) {
      isOpen.value = true
      isOpenMobile.value = true
    }
  },
  { immediate: true }
)
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

const questionIDs = ['03-PA', '07-PA', '08-PA', '09-FoC']
const questionLabels = ref([])
const loadingQuestions = ref(true)

const fetchQuestions = async () => {
  loadingQuestions.value = true
  try {
    const config = useRuntimeConfig()
    const labels = []
    for (const id of questionIDs) {
      const response = await fetch(
        `${config.public.apiBaseUrl}/search/full_table`,
        {
          method: 'POST',
          headers: {
            authorization: `Bearer ${config.public.FASTAPI}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            table: 'Questions',
            filters: [{ column: 'ID', value: id }],
          }),
        }
      )
      if (!response.ok) {
        const errorText = await response.text()
        // console.error(`API error for ID ${id}:`, errorText)
        labels.push(id)
        continue
      }
      const data = await response.json()
      labels.push(data[0]?.Question || id)
    }
    questionLabels.value = labels
  } catch (error) {
    // console.error('Error fetching questions:', error)
    questionLabels.value = questionIDs // fallback to IDs
  } finally {
    loadingQuestions.value = false
  }
}

onMounted(fetchQuestions)

// Static sample data as computed property
// const questionLabels = [
//   'Is the principle of party autonomy in respect of choice of law in international commercial contracts widely accepted in this jurisdiction?', // 03-PA
//   'Is a connection required between the chosen law and the parties or their transaction? ', // 07-PA
//   'Are the parties prevented from choosing the law of a third country with which there is no connection (a “neutral law”)?', // 08-PA
//   'Are the parties allowed to choose non-State law (“rules of law”) to govern their contract?', // 09-FoC
// ]
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
  grid-template-columns: 1.5fr 1fr 1fr 1fr;
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
  margin-bottom: 1.5rem;
  line-height: 2;
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
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 0 1.5rem;
  width: 100%;
}
.jc-table-row {
  display: contents;
}
.jc-table-cell {
  padding: 0.75rem 0 0.75rem 0;
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
