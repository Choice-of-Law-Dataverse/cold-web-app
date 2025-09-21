<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <!-- Filters and Results Header -->
        <div
          class="filters-header mt-[-24px] !mb-2 ml-[-1px] flex flex-col md:flex-row md:justify-between md:items-center gap-4"
        >
          <!-- Filter Controls -->
          <div class="flex flex-col sm:flex-row gap-5 w-full">
            <SearchFilters
              :options="jurisdictions || []"
              v-model="currentJurisdictionFilter"
              class="w-full lg:w-60 flex-shrink-0"
              :showAvatars="true"
              :multiple="false"
              :highlight-jurisdictions="true"
              :placeholder="'Jurisdiction'"
            />
            <SearchFilters
              :options="themeOptions"
              v-model="currentThemeFilter"
              class="w-full lg:w-60 flex-shrink-0"
              :placeholder="'Themes'"
            />
            <SearchFilters
              :options="typeOptions"
              v-model="currentTypeFilter"
              class="w-full lg:w-60 flex-shrink-0"
              :placeholder="'Types'"
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

          <!-- Results Count and Sort -->
          <span
            class="text-right md:text-left w-full md:w-auto whitespace-nowrap result-value-small flex items-center gap-2 results-margin-fix"
          >
            <template v-if="!loading">
              <template v-if="props.totalMatches > 1">
                <span class="mr-[-2px]">
                  {{ formattedTotalMatches }} results sorted by
                </span>
                <!-- Hidden Measurement Element -->
                <span
                  ref="measureRef"
                  class="absolute opacity-0 pointer-events-none select-none font-inherit text-base"
                  style="
                    position: absolute;
                    left: -9999px;
                    top: 0;
                    white-space: pre;
                  "
                  aria-hidden="true"
                >
                  {{ selectValue }}
                </span>
                <!-- Sort Selector -->
                <USelect
                  ref="selectRef"
                  variant="none"
                  :options="['relevance', 'date']"
                  :model-value="selectValue"
                  :style="{
                    color: 'var(--color-cold-purple)',
                    width: selectWidth,
                    textAlign: 'right',
                    minWidth: 'unset',
                    maxWidth: 'none',
                    marginLeft: '0',
                    paddingLeft: '0',
                  }"
                  class="flex-shrink-0 text-right"
                  @update:modelValue="handleSortChange"
                >
                  <template #trailing>
                    <UIcon
                      name="i-material-symbols:keyboard-arrow-down"
                      class="w-5 h-5"
                      style="color: var(--color-cold-purple)"
                    />
                  </template>
                </USelect>
              </template>
              <span v-else style="margin-right: 0; padding-right: 0">
                {{ formattedTotalMatches }} {{ resultLabel }}
              </span>
            </template>
            <!-- Loading placeholder to maintain space -->
            <span v-else class="opacity-0" style="height: 1.5rem">
              <!-- Invisible placeholder to maintain layout -->
            </span>
          </span>
        </div>

        <!-- Results Content -->
        <div class="results-content mt-4">
          <!-- Loading State -->
          <div v-if="loading && !allResults.length" class="results-grid">
            <LoadingCard v-for="n in 6" :key="`loading-${n}`" />
          </div>

          <!-- No Results State -->
          <NoSearchResults v-else-if="!loading && !allResults.length" />

          <!-- Results Grid -->
          <template v-else>
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
              <!-- Loading More Indicator -->
              <LoadingCard
                v-if="loading && allResults.length"
                class="text-center py-4"
              />
            </div>

            <!-- Load More Button -->
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

            <!-- Search Info Link -->
            <div v-if="!loading" class="result-value-small text-center pt-4">
              <UButton
                to="https://choice-of-law-dataverse.github.io/search-algorithm"
                variant="link"
                target="_blank"
              >
                Learn How the Search Works
              </UButton>
              <UIcon
                name="i-material-symbols:open-in-new"
                class="inline-block ml-[-6px]"
                style="
                  color: var(--color-cold-purple);
                  position: relative;
                  top: 2px;
                "
              />
            </div>
          </template>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed, ref, watch, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSearchFilters } from '@/composables/useSearchFilters'
import importedThemeOptions from '@/assets/themeOptions.json'
import importedTypeOptions from '@/assets/typeOptions.json'

// Component imports
import ResultCard from '@/components/search-results/ResultCard.vue'
import LegislationCard from '@/components/search-results/LegislationCard.vue'
import RegionalInstrumentCard from '@/components/search-results/RegionalInstrumentCard.vue'
import InternationalInstrumentCard from '@/components/search-results/InternationalInstrumentCard.vue'
import LiteratureCard from '@/components/search-results/LiteratureCard.vue'
import CourtDecisionCard from '@/components/search-results/CourtDecisionCard.vue'
import AnswerCard from '@/components/search-results/AnswerCard.vue'
import SearchFilters from '@/components/search-results/SearchFilters.vue'
import NoSearchResults from '@/components/search-results/NoSearchResults.vue'
import LoadingCard from '@/components/layout/LoadingCard.vue'

// Component mapping for different result types
const resultComponentMap = {
  'Domestic Instruments': LegislationCard,
  'Regional Instruments': RegionalInstrumentCard,
  'International Instruments': InternationalInstrumentCard,
  'Court Decisions': CourtDecisionCard,
  Answers: AnswerCard,
  Literature: LiteratureCard,
}

const getResultComponent = (source_table) =>
  resultComponentMap[source_table] || ResultCard

// Props and emits
const props = defineProps({
  data: {
    type: Object,
    default: () => ({ tables: {} }),
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

// Router setup
const route = useRoute()
const router = useRouter()

// Initialize search filters
const {
  currentJurisdictionFilter,
  currentThemeFilter,
  currentTypeFilter,
  selectValue,
  hasActiveFilters,
  buildFilterObject,
  resetFilters: resetFilterValues,
  syncFiltersFromQuery,
} = useSearchFilters(route.query)

// UI state
const selectWidth = ref('auto')
const measureRef = ref(null)

// Filter options
const themeOptions = importedThemeOptions
const typeOptions = importedTypeOptions

// Computed values
const allResults = computed(() => {
  if (!props.data?.tables) return []
  return Object.values(props.data.tables)
})

const formattedTotalMatches = computed(() =>
  props.totalMatches.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '’')
)
const resultLabel = computed(() =>
  props.totalMatches === 1 ? 'result' : 'results'
)

// Methods
const updateFilters = async (filters) => {
  emit('update:filters', filters)
  await router.push({
    path: route.path,
    query: { ...filters },
  })
}

const handleSortChange = async (val) => {
  const sortValue = val || 'relevance'
  selectValue.value = sortValue
  // Only update the sortBy parameter without triggering other filter updates
  emit('update:filters', { ...props.filters, sortBy: sortValue })
  updateSelectWidth()
}

const resetFilters = async () => {
  resetFilterValues()
  await updateFilters({ sortBy: route.query.sortBy || 'relevance' })
}

const updateSelectWidth = () => {
  nextTick(() => {
    if (measureRef.value) {
      selectWidth.value = measureRef.value.offsetWidth + 36 + 'px'
    }
  })
}

// Data fetching via composable
import { useJurisdictions } from '@/composables/useJurisdictions'
const { data: jurisdictions } = useJurisdictions()

// Watchers
watch(
  [currentJurisdictionFilter, currentThemeFilter, currentTypeFilter],
  async ([jurisdiction, theme, type]) => {
    if (!jurisdiction && !theme && !type) return
    await updateFilters(
      buildFilterObject(jurisdiction, theme, type, selectValue.value)
    )
  },
  { deep: true }
)

watch(
  () => route.query,
  () => {
    syncFiltersFromQuery(route.query)
    updateSelectWidth()
  },
  { immediate: true }
)

// Initialization
onMounted(async () => {
  syncFiltersFromQuery(route.query)
  updateSelectWidth()
})
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

.results-margin-fix {
  margin-top: 1.5rem !important;
}

::v-deep(
  .u-select .u-select__icon,
  .u-select .u-select__caret,
  .u-select .n-base-suffix .n-base-suffix__arrow,
  .u-select .n-base-suffix__arrow
) {
  color: var(--color-cold-purple) !important;
  fill: var(--color-cold-purple) !important;
}
</style>
