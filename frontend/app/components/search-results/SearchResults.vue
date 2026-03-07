<template>
  <SearchResultsHeader
    :filters="props.filters"
    :total-matches="props.totalMatches"
    :loading="props.loading"
    :has-query="props.hasQuery"
    @update:filters="emit('update:filters', $event)"
  />

  <SearchResultsGrid
    :results="allResults"
    :loading="props.loading"
    :can-load-more="props.canLoadMore"
    :has-query="props.hasQuery"
    @load-more="emit('load-more')"
  />
</template>

<script setup lang="ts">
import { computed } from "vue";
import SearchResultsHeader from "@/components/search-results/SearchResultsHeader.vue";
import SearchResultsGrid from "@/components/search-results/SearchResultsGrid.vue";
import type { SearchFilters } from "@/types/api";

interface SearchData {
  tables: Record<string, unknown>[];
}

const props = withDefaults(
  defineProps<{
    data?: SearchData;
    filters: SearchFilters;
    totalMatches?: number;
    loading?: boolean;
    canLoadMore?: boolean;
    hasQuery?: boolean;
  }>(),
  {
    data: () => ({ tables: [] }),
    totalMatches: 0,
    loading: false,
    canLoadMore: false,
    hasQuery: false,
  },
);

const emit = defineEmits<{
  "update:filters": [filters: SearchFilters];
  "load-more": [];
}>();

const allResults = computed((): Record<string, unknown>[] => {
  if (!props.data?.tables) return [];
  return props.data.tables;
});
</script>
