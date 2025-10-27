<template>
  <!-- Filters and Results Header -->
  <div class="filters-header !mb-2 ml-[-1px] mt-[-24px] flex flex-col gap-4">
    <!-- Filter Controls -->
    <div class="flex w-full flex-col flex-wrap gap-5 sm:flex-row">
      <SearchFilters
        v-model="currentJurisdictionFilter"
        :options="jurisdictions || []"
        class="w-full flex-shrink-0 lg:w-60"
        :show-avatars="true"
        :multiple="false"
        :highlight-jurisdictions="true"
        :placeholder="'Jurisdiction'"
      />
      <SearchFilters
        v-model="currentThemeFilter"
        :options="themeOptions"
        class="w-full flex-shrink-0 lg:w-60"
        :placeholder="'Themes'"
      />
      <SearchFilters
        v-model="currentTypeFilter"
        :options="typeOptions"
        class="w-full flex-shrink-0 lg:w-60"
        :placeholder="'Types'"
      />
      <UButton
        v-if="hasActiveFilters"
        variant="link"
        class="link-button w-full sm:w-auto"
        @click="resetFilters"
      >
        Reset
      </UButton>
    </div>

    <!-- Results Count and Sort -->
    <div
      class="result-value-small results-margin-fix flex w-full items-center gap-2 whitespace-nowrap"
    >
      <template v-if="!loading">
        <template v-if="props.totalMatches > 1">
          <span class="mr-[-2px]">
            {{ formattedTotalMatches }} results sorted by
          </span>
          <!-- Hidden Measurement Element -->
          <span
            ref="measureRef"
            class="font-inherit pointer-events-none absolute select-none text-base opacity-0"
            style="position: absolute; left: -9999px; top: 0; white-space: pre"
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
            @update:model-value="handleSortChange"
          >
            <template #trailing>
              <UIcon
                name="i-material-symbols:keyboard-arrow-down"
                class="h-5 w-5 text-cold-purple"
              />
            </template>
          </USelect>
        </template>
        <span v-else class="mr-0 pr-0">
          {{ formattedTotalMatches }} {{ resultLabel }}
        </span>
      </template>
    </div>
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
            :result-data="resultData"
          />
        </div>
        <!-- Loading More Indicator -->
        <LoadingCard
          v-if="loading && allResults.length"
          class="py-4 text-center"
        />
      </div>

      <!-- Load More Button -->
      <div v-if="props.canLoadMore && !loading" class="mb-4 mt-16 text-center">
        <UButton
          native-type="button"
          class="suggestion-button"
          variant="link"
          icon="i-material-symbols:arrow-cool-down"
          :disabled="props.loading"
          @click.prevent="emit('load-more')"
        >
          Load More Results
        </UButton>
      </div>

      <!-- Search Info Link -->
      <div v-if="!loading" class="result-value-small pt-4 text-center">
        <UButton
          to="https://choice-of-law-dataverse.github.io/search-algorithm"
          variant="link"
          target="_blank"
        >
          Learn How the Search Works
        </UButton>
        <UIcon
          name="i-material-symbols:open-in-new"
          class="ml-[-6px] inline-block"
          style="color: var(--color-cold-purple); position: relative; top: 2px"
        />
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useSearchFilters } from "@/composables/useSearchFilters";
import importedThemeOptions from "@/assets/themeOptions.json";
import importedTypeOptions from "@/assets/typeOptions.json";

// Component imports
import ResultCard from "@/components/search-results/ResultCard.vue";
import LegislationCard from "@/components/search-results/LegislationCard.vue";
import RegionalInstrumentCard from "@/components/search-results/RegionalInstrumentCard.vue";
import InternationalInstrumentCard from "@/components/search-results/InternationalInstrumentCard.vue";
import LiteratureCard from "@/components/search-results/LiteratureCard.vue";
import CourtDecisionCard from "@/components/search-results/CourtDecisionCard.vue";
import AnswerCard from "@/components/search-results/AnswerCard.vue";
import SearchFilters from "@/components/search-results/SearchFilters.vue";
import NoSearchResults from "@/components/search-results/NoSearchResults.vue";
import LoadingCard from "@/components/layout/LoadingCard.vue";

// Data fetching via composable
import { useJurisdictions } from "@/composables/useJurisdictions";

// Component mapping for different result types
const resultComponentMap = {
  "Domestic Instruments": LegislationCard,
  "Regional Instruments": RegionalInstrumentCard,
  "International Instruments": InternationalInstrumentCard,
  "Court Decisions": CourtDecisionCard,
  Answers: AnswerCard,
  Literature: LiteratureCard,
};

const getResultComponent = (source_table) =>
  resultComponentMap[source_table] || ResultCard;

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
});

const emit = defineEmits(["update:filters", "load-more"]);

// Router setup
const route = useRoute();
const router = useRouter();

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
} = useSearchFilters(route.query);

// UI state
const selectWidth = ref("auto");
const measureRef = ref(null);

// Filter options
const themeOptions = importedThemeOptions;
const typeOptions = importedTypeOptions;

// Computed values
const allResults = computed(() => {
  if (!props.data?.tables) return [];
  return Object.values(props.data.tables);
});

const formattedTotalMatches = computed(() =>
  props.totalMatches.toString().replace(/\B(?=(\d{3})+(?!\d))/g, "’"),
);
const resultLabel = computed(() =>
  props.totalMatches === 1 ? "result" : "results",
);

// Methods
const updateFilters = async (filters) => {
  emit("update:filters", filters);
  await router.push({
    path: route.path,
    query: { ...filters },
  });
};

const handleSortChange = async (val) => {
  const sortValue = val || "relevance";
  selectValue.value = sortValue;
  // Only update the sortBy parameter without triggering other filter updates
  emit("update:filters", { ...props.filters, sortBy: sortValue });
  updateSelectWidth();
};

const resetFilters = async () => {
  resetFilterValues();
  await updateFilters({ sortBy: route.query.sortBy || "relevance" });
};

const updateSelectWidth = () => {
  nextTick(() => {
    if (measureRef.value) {
      selectWidth.value = measureRef.value.offsetWidth + 36 + "px";
    }
  });
};
const { data: jurisdictions } = useJurisdictions();

// Watchers
watch(
  [currentJurisdictionFilter, currentThemeFilter, currentTypeFilter],
  async ([jurisdiction, theme, type]) => {
    if (!jurisdiction && !theme && !type) return;
    await updateFilters(
      buildFilterObject(jurisdiction, theme, type, selectValue.value),
    );
  },
  { deep: true },
);

watch(
  () => route.query,
  () => {
    syncFiltersFromQuery(route.query);
    updateSelectWidth();
  },
  { immediate: true },
);

// Initialization
onMounted(async () => {
  syncFiltersFromQuery(route.query);
  updateSelectWidth();
});
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
