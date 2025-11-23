<template>
  <div>
    <div v-if="apiError" class="error-message">
      <p>
        We're sorry, but we encountered an error while processing your search.
        Please try again later.
      </p>
      <p class="error-details">{{ apiError }}</p>
    </div>
    <EmptySearchState v-else-if="!searchQuery && !hasActiveFilters" />
    <SearchResults
      v-else
      :data="{ tables: searchResults }"
      :total-matches="totalMatches"
      :loading="loading"
      :can-load-more="hasNextPage && !isFetchingNextPage"
      @load-more="loadMoreResults"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";
import SearchResults from "@/components/search-results/SearchResults.vue";
import EmptySearchState from "@/components/search-results/EmptySearchState.vue";
import { useSearch } from "@/composables/useSearch";
import { useHead, useSeoMeta } from "#imports";

useSeoMeta({
  robots: "noindex, follow",
});

const route = useRoute();

// Parse filters directly from route query
const searchQuery = computed(() => (route.query.q as string) || "");

const hasActiveFilters = computed(
  () => !!(route.query.jurisdiction || route.query.theme || route.query.type),
);

// Search parameters for the API - read directly from route
const searchParams = computed(() => ({
  filters: {
    jurisdiction: route.query.jurisdiction as string | undefined,
    theme: route.query.theme as string | undefined,
    type: route.query.type as string | undefined,
    sortBy: ((route.query.sortBy as string) === "date"
      ? "date"
      : "relevance") as "date" | "relevance",
  },
  pageSize: 10,
  query: searchQuery.value,
  enabledOverride: true,
}));

// Fetch search results
const {
  data: searchData,
  isLoading,
  error,
  fetchNextPage,
  hasNextPage,
  isFetchingNextPage,
} = useSearch(searchParams);

// Computed values from search data
const searchResults = computed(() => {
  if (!searchData.value?.pages) return [];
  return searchData.value.pages.flatMap((page) => page.results);
});

const totalMatches = computed(() => {
  return searchData.value?.pages?.[0]?.totalMatches || 0;
});

const loading = computed(() => isLoading.value || isFetchingNextPage.value);
const apiError = computed(() => error.value?.message || null);

// Update page title based on search query
watch(
  searchQuery,
  (newQuery) => {
    useHead({
      title:
        newQuery && newQuery.trim() ? `${newQuery} — CoLD` : "Search — CoLD",
    });
  },
  { immediate: true },
);

// Load more results handler
function loadMoreResults() {
  if (hasNextPage.value && !isFetchingNextPage.value) {
    fetchNextPage();
  }
}
</script>

<style scoped>
.error-message {
  padding: 2rem;
  margin: 2rem;
  background-color: var(--color-cold-red-light);
  border: 1px solid var(--color-cold-red);
  border-radius: 0.5rem;
  color: var(--color-cold-red);
}

.error-details {
  margin-top: 1rem;
  font-size: 0.875rem;
  opacity: 0.8;
}
</style>
