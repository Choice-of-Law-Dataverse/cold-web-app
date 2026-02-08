<template>
  <div class="filters-header mt-[-24px] !mb-2 ml-[-1px] flex flex-col gap-4">
    <div class="flex w-full flex-col flex-wrap gap-5 sm:flex-row">
      <SearchFilters
        :model-value="currentJurisdictionFilter"
        :options="jurisdictions || []"
        class="w-full flex-shrink-0 lg:w-60"
        :show-avatars="true"
        :multiple="false"
        :highlight-jurisdictions="true"
        :placeholder="'Jurisdiction'"
        @update:model-value="currentJurisdictionFilter = $event"
      />
      <SearchFilters
        :model-value="currentThemeFilter"
        :options="themeOptions"
        class="w-full flex-shrink-0 lg:w-60"
        :placeholder="'Themes'"
        :searchable="false"
        @update:model-value="currentThemeFilter = $event"
      />
      <SearchFilters
        :model-value="currentTypeFilter"
        :options="typeOptions"
        class="w-full flex-shrink-0 lg:w-60"
        :multiple="false"
        :placeholder="'Types'"
        :searchable="false"
        @update:model-value="currentTypeFilter = $event"
      />
      <UButton
        v-if="hasActiveFilters"
        variant="link"
        class="w-full sm:w-auto"
        @click="resetFilters"
      >
        Reset
      </UButton>
    </div>

    <div
      v-if="props.hasQuery || hasActiveFilters"
      class="result-value-small results-margin-fix flex w-full items-center gap-2 whitespace-nowrap"
    >
      <template v-if="!props.loading">
        <template v-if="props.totalMatches > 1">
          <span class="mr-[-2px]">
            {{ formattedTotalMatches }} results sorted by
          </span>
          <span
            ref="measureRef"
            class="font-inherit pointer-events-none absolute text-base opacity-0 select-none"
            style="position: absolute; left: -9999px; top: 0; white-space: pre"
            aria-hidden="true"
          >
            {{ selectValue }}
          </span>
          <USelect
            ref="selectRef"
            variant="none"
            :items="['relevance', 'date']"
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
</template>

<script setup>
import { computed, ref, watch, onMounted, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useSearchFilters } from "@/composables/useSearchFilters";
import importedThemeOptions from "@/assets/themeOptions.json";
import importedTypeOptions from "@/assets/typeOptions.json";
import SearchFilters from "@/components/search-results/SearchFilters.vue";
import { useJurisdictions } from "@/composables/useJurisdictions";

const props = defineProps({
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
  hasQuery: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:filters"]);

const route = useRoute();
const router = useRouter();

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

const selectWidth = ref("auto");
const measureRef = ref(null);

const themeOptions = importedThemeOptions;
const typeOptions = importedTypeOptions;

const formattedTotalMatches = computed(() =>
  props.totalMatches.toString().replace(/\B(?=(\d{3})+(?!\d))/g, "'"),
);
const resultLabel = computed(() =>
  props.totalMatches === 1 ? "result" : "results",
);

const { data: jurisdictions } = useJurisdictions();

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
  emit("update:filters", { ...props.filters, sortBy: sortValue });
  updateSelectWidth();
};

const resetFilters = async () => {
  resetFilterValues();
  emit("update:filters", { sortBy: route.query.sortBy || "relevance" });
  await router.push({
    path: route.path,
    query: { sortBy: route.query.sortBy || "relevance" },
  });
};

const updateSelectWidth = () => {
  nextTick(() => {
    if (measureRef.value) {
      selectWidth.value = measureRef.value.offsetWidth + 36 + "px";
    }
  });
};

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

onMounted(async () => {
  syncFiltersFromQuery(route.query);
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
  font-weight: 600;
}

.results-margin-fix {
  margin-top: 1.5rem;
}
</style>
