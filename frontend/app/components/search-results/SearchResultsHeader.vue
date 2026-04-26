<template>
  <div class="search-results-header">
    <div class="entity-filters">
      <div class="entity-filters__control">
        <JurisdictionSelectMenu
          v-if="jurisdictions"
          :jurisdictions="jurisdictions"
          :model-value="jurisdictionOption"
          placeholder="Jurisdiction"
          @update:model-value="onJurisdictionChange"
        />
      </div>

      <div class="entity-filters__control">
        <USelectMenu
          v-model="themeValues"
          multiple
          :items="themeOptions"
          placeholder="Theme"
          size="xl"
          class="w-56"
          :ui="{
            content:
              'max-h-(--reka-combobox-content-available-height) w-max min-w-(--reka-combobox-trigger-width)',
            item: 'data-highlighted:bg-transparent',
          }"
        >
          <template #item-label="{ item }">
            <span class="schip schip--theme schip--static">
              <span class="schip-tag" aria-hidden="true">
                <UIcon name="i-lucide:bookmark" />
              </span>
              <span class="schip-text">{{ item }}</span>
            </span>
          </template>
        </USelectMenu>
      </div>

      <div class="entity-filters__control">
        <USelectMenu
          v-model="typeValues"
          multiple
          :items="typeOptions"
          placeholder="Type"
          size="xl"
          class="w-56"
          :ui="{
            content:
              'max-h-(--reka-combobox-content-available-height) w-max min-w-(--reka-combobox-trigger-width)',
            item: 'data-highlighted:bg-transparent',
          }"
        >
          <template #item-label="{ item }">
            <span
              :class="[
                'schip',
                'schip--type',
                'schip--static',
                getLabelColorClass(item),
              ]"
            >
              <span class="schip-tag" aria-hidden="true">
                <UIcon name="i-lucide:tag" />
              </span>
              <span class="schip-text">{{ item }}</span>
            </span>
          </template>
        </USelectMenu>
      </div>

      <div v-if="hasActiveFilters" class="entity-filters__reset">
        <UButton
          variant="ghost"
          size="sm"
          :icon="ICON_CLEAR"
          @click="resetFilters"
        >
          Clear filters
        </UButton>
      </div>
    </div>

    <div
      v-if="props.hasQuery || hasActiveFilters"
      class="result-value-small flex w-full items-center gap-2 whitespace-nowrap"
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

<script setup lang="ts">
import { computed, ref, watch, onMounted, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useSearchFilters } from "@/composables/useSearchFilters";
import importedThemeOptions from "@/assets/themeOptions.json";
import importedTypeOptions from "@/assets/typeOptions.json";
import JurisdictionSelectMenu from "@/components/jurisdiction/JurisdictionSelectMenu.vue";
import {
  useJurisdictions,
  useJurisdictionLookup,
} from "@/composables/useJurisdictions";
import { useScreenAnnouncer } from "@/composables/useScreenAnnouncer";
import { getLabelColorClass } from "@/config/entityRegistry";
import type {
  FilterObjectOption,
  FilterOption,
  SearchFilters as SearchFiltersType,
} from "@/types/api";
import type { JurisdictionOption } from "@/types/analyzer";

const ICON_CLEAR = "i-material-symbols:close";

const props = withDefaults(
  defineProps<{
    filters: SearchFiltersType;
    totalMatches?: number;
    loading?: boolean;
    hasQuery?: boolean;
  }>(),
  {
    totalMatches: 0,
    loading: false,
    hasQuery: false,
  },
);

const emit = defineEmits<{
  "update:filters": [filters: SearchFiltersType];
}>();

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
const measureRef = ref<HTMLElement | null>(null);

const themeOptions = importedThemeOptions;
const typeOptions = importedTypeOptions;

const formattedTotalMatches = computed(() =>
  props.totalMatches.toString().replace(/\B(?=(\d{3})+(?!\d))/g, "'"),
);
const resultLabel = computed(() =>
  props.totalMatches === 1 ? "result" : "results",
);

const { data: jurisdictions } = useJurisdictions();
const { findJurisdictionByName } = useJurisdictionLookup();
const { announce } = useScreenAnnouncer();

const optionLabel = (item: FilterOption): string =>
  typeof item === "object" && item !== null ? item.label : String(item);

const jurisdictionOption = computed<JurisdictionOption | undefined>(() => {
  const first = currentJurisdictionFilter.value[0];
  if (!first) return undefined;
  const label = optionLabel(first);
  return findJurisdictionByName(label);
});

function onJurisdictionChange(jurisdiction: JurisdictionOption | undefined) {
  if (!jurisdiction) {
    currentJurisdictionFilter.value = [];
    return;
  }
  const next: FilterObjectOption = {
    label: jurisdiction.label,
    coldId: jurisdiction.coldId,
  };
  currentJurisdictionFilter.value = [next];
}

const themeValues = computed<string[]>({
  get() {
    return currentThemeFilter.value.map(optionLabel);
  },
  set(values) {
    currentThemeFilter.value = values;
  },
});

const typeValues = computed<string[]>({
  get() {
    return currentTypeFilter.value.map(optionLabel);
  },
  set(values) {
    currentTypeFilter.value = values;
  },
});

watch(
  () => [props.totalMatches, props.loading],
  ([total, loading]) => {
    if (!loading && total !== undefined) {
      announce(`${total} ${total === 1 ? "result" : "results"} found`);
    }
  },
);

const updateFilters = async (filters: SearchFiltersType) => {
  emit("update:filters", filters);
  await router.push({
    path: route.path,
    query: { ...filters },
  });
};

const handleSortChange = async (val: string) => {
  const sortValue = (val || "relevance") as SearchFiltersType["sortBy"];
  selectValue.value = sortValue ?? "relevance";
  await updateFilters({ ...props.filters, sortBy: sortValue });
  updateSelectWidth();
};

const resetFilters = async () => {
  resetFilterValues();
  const sortBy = String(
    route.query.sortBy || "relevance",
  ) as SearchFiltersType["sortBy"];
  emit("update:filters", { sortBy });
  await router.push({
    path: route.path,
    query: { sortBy },
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
.search-results-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: -24px;
}

.entity-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.entity-filters__control {
  min-width: 14rem;
}

.entity-filters__reset {
  display: flex;
  align-items: center;
}

.result-value-small {
  font-weight: 600;
  margin-top: 0.5rem;
}
</style>
