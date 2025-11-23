<template>
  <!-- Filters and Results Header -->
  <div class="filters-header mt-[-24px] !mb-2 ml-[-1px] flex flex-col gap-4">
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
        :multiple="false"
        :placeholder="'Themes'"
      />
      <SearchFilters
        v-model="currentTypeFilter"
        :options="typeOptions"
        class="w-full flex-shrink-0 lg:w-60"
        :multiple="false"
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
            class="font-inherit pointer-events-none absolute text-base opacity-0 select-none"
            style="position: absolute; left: -9999px; top: 0; white-space: pre"
            aria-hidden="true"
          >
            {{ selectValue }}
          </span>
          <!-- Sort Selector -->
          <USelect
            ref="selectRef"
            v-model="selectValue"
            variant="none"
            :options="['relevance', 'date']"
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
                class="text-cold-purple h-5 w-5"
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
      <div v-if="props.canLoadMore && !loading" class="mt-16 mb-4 text-center">
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

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref, watch } from "vue";
import { useSearchFilters } from "@/composables/useSearchFilters";
import importedThemeOptions from "@/assets/themeOptions.json";
import importedTypeOptions from "@/assets/typeOptions.json";

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

import { useJurisdictions } from "@/composables/useJurisdictions";

const resultComponentMap = {
  "Domestic Instruments": LegislationCard,
  "Regional Instruments": RegionalInstrumentCard,
  "International Instruments": InternationalInstrumentCard,
  "Court Decisions": CourtDecisionCard,
  Answers: AnswerCard,
  Literature: LiteratureCard,
};

const getResultComponent = (source_table: string) =>
  resultComponentMap[source_table as keyof typeof resultComponentMap] ||
  ResultCard;

const props = defineProps({
  data: {
    type: Object,
    default: () => ({ tables: {} }),
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

const emit = defineEmits(["load-more"]);

// Use the search filters composable
const {
  currentJurisdictionFilter,
  currentThemeFilter,
  currentTypeFilter,
  selectValue,
  hasActiveFilters,
  resetFilters,
} = useSearchFilters();

const route = useRoute();

// Sync filters from URL on mount
const parseQueryParam = (param: string | string[] | undefined): string[] => {
  if (!param) return [];
  if (Array.isArray(param)) return param;
  return param.split(",").filter(Boolean);
};

onMounted(() => {
  currentJurisdictionFilter.value = parseQueryParam(
    route.query.jurisdiction as string,
  );
  currentThemeFilter.value = parseQueryParam(route.query.theme as string);
  currentTypeFilter.value = parseQueryParam(route.query.type as string);
  selectValue.value =
    (route.query.sortBy as string) === "date" ? "date" : "relevance";
  stopFilterWatcher = watch(
    [
      currentJurisdictionFilter,
      currentThemeFilter,
      currentTypeFilter,
      selectValue,
    ],
    () => {
      // Only update local state, do not call router.replace
      // If you want to update the URL, do it on explicit user action only
    },
    { deep: true },
  );
});

let stopFilterWatcher: (() => void) | null = null;

onMounted(() => {
  stopFilterWatcher = watch(
    [
      currentJurisdictionFilter,
      currentThemeFilter,
      currentTypeFilter,
      selectValue,
    ],
    () => {
      // Only update local state, do not call router.replace
      // If you want to update the URL, do it on explicit user action only
    },
    { deep: true },
  );
});

onBeforeUnmount(() => {
  if (stopFilterWatcher) stopFilterWatcher();
});

const selectWidth = ref("auto");
const measureRef = ref<HTMLElement | null>(null);

const themeOptions = importedThemeOptions;
const typeOptions = importedTypeOptions;

const allResults = computed(() => {
  if (!props.data?.tables) return [];
  return Object.values(props.data.tables) as Array<
    Record<string, unknown> & { source_table: string }
  >;
});

const formattedTotalMatches = computed(() =>
  props.totalMatches.toString().replace(/\B(?=(\d{3})+(?!\d))/g, "’"),
);
const resultLabel = computed(() =>
  props.totalMatches === 1 ? "result" : "results",
);

const handleSortChange = () => {
  // Sort value updates via v-model, watcher handles URL
  updateSelectWidth();
};

const updateSelectWidth = () => {
  nextTick(() => {
    if (measureRef.value) {
      selectWidth.value = measureRef.value.offsetWidth + 36 + "px";
    }
  });
};
const { data: jurisdictions } = useJurisdictions();

onMounted(() => {
  updateSelectWidth();
});
</script>

<style scoped>
.filters-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
}

.filters-header h2 {
  margin: 0;
  padding-bottom: 0;
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
