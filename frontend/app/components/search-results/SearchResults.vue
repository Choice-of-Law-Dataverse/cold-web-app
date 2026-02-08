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

<script setup>
import { computed } from "vue";
import SearchResultsHeader from "@/components/search-results/SearchResultsHeader.vue";
import SearchResultsGrid from "@/components/search-results/SearchResultsGrid.vue";

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
  hasQuery: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:filters", "load-more"]);

const allResults = computed(() => {
  if (!props.data?.tables) return [];
  return Object.values(props.data.tables);
});
</script>
