<template>
  <div>
    <h1 class="sr-only">Search Results</h1>
    <div v-if="apiError" role="alert" class="error-message">
      <p>
        We're sorry, but we encountered an error while processing your search.
        Please try again later.
      </p>
      <p class="error-details">{{ apiError }}</p>
    </div>
    <SearchResults
      v-else
      v-model:filters="filter"
      :data="{ tables: searchResults }"
      :total-matches="totalMatches"
      :loading="loading"
      :can-load-more="hasNextPage && !isFetchingNextPage"
      :has-query="!!searchQuery"
      @load-more="loadMoreResults"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed, nextTick } from "vue";
import { useRoute } from "vue-router";
import SearchResults from "@/components/search-results/SearchResults.vue";
import { useSearch } from "@/composables/useSearch";
import { useHead, useSeoMeta } from "#imports";
import type { SearchFilters, SearchParams } from "@/types/api";

useSeoMeta({
  robots: "noindex, follow",
});

const route = useRoute();
const searchQuery = ref(String(route.query.q || ""));

const filter = ref<SearchFilters>({
  jurisdiction: route.query.jurisdiction as string | undefined,
  sortBy: (route.query.sortBy as SearchFilters["sortBy"]) || "relevance",
  theme: route.query.theme as string | undefined,
  type: route.query.type as string | undefined,
});

const searchText = ref(String(route.query.q || ""));

const isInitialized = ref(false);

const searchParams = computed<SearchParams>(() => {
  if (!isInitialized.value) {
    return {
      filters: {},
      pageSize: 10,
      query: "",
      enabledOverride: false,
    };
  }

  return {
    filters: filter.value,
    pageSize: 10,
    query: searchQuery.value,
  };
});

const {
  data: searchData,
  isLoading,
  error,
  fetchNextPage,
  hasNextPage,
  isFetchingNextPage,
} = useSearch(searchParams);

const searchResults = computed(() => {
  if (!searchData.value?.pages) return [];
  return searchData.value.pages.flatMap((page) => page.results);
});

const totalMatches = computed(() => {
  return searchData.value?.pages?.[0]?.totalMatches || 0;
});

const loading = computed(() => isLoading.value || isFetchingNextPage.value);
const apiError = computed(() => error.value?.message || null);

watch(searchQuery, (newQuery) => {
  searchText.value = String(newQuery || "");
});

watch(
  searchQuery,
  (newQuery) => {
    const q = String(newQuery || "");
    useHead({
      title: q.trim() ? `${q} — CoLD` : "Search — CoLD",
    });
  },
  { immediate: true },
);

watch(
  filter,
  (newFilters, oldFilters) => {
    if (route.name !== "search") return;
    if (JSON.stringify(newFilters) === JSON.stringify(oldFilters)) return;

    const query: Record<string, string | undefined> = {
      q: String(route.query.q || ""),
      jurisdiction: newFilters.jurisdiction,
      sortBy: newFilters.sortBy,
      theme: newFilters.theme,
      type: newFilters.type,
    };

    if (!String(searchText.value).trim()) {
      delete query.q;
    }

    const cleanedQuery: Record<string, string> = {};
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined) {
        cleanedQuery[key] = value;
      }
    }

    navigateTo({ path: "/search", query: cleanedQuery }, { replace: true });
  },
  { deep: true },
);

watch(
  () => route.query,
  (newQuery) => {
    if (route.name !== "search") return;

    searchQuery.value = String(newQuery.q || "");

    const newFilters: SearchFilters = {};
    if (newQuery.jurisdiction)
      newFilters.jurisdiction = String(newQuery.jurisdiction);
    if (newQuery.sortBy)
      newFilters.sortBy = String(newQuery.sortBy) as SearchFilters["sortBy"];
    if (newQuery.theme) newFilters.theme = String(newQuery.theme);
    if (newQuery.type) newFilters.type = String(newQuery.type);

    if (JSON.stringify(newFilters) !== JSON.stringify(filter.value)) {
      filter.value = newFilters;
    }

    if (!isInitialized.value) {
      nextTick(() => {
        isInitialized.value = true;
      });
    }
  },
  { deep: true, immediate: true },
);

function loadMoreResults() {
  if (hasNextPage.value && !isFetchingNextPage.value) {
    fetchNextPage();
  }
}

onMounted(() => {
  searchText.value = String(route.query.q || "");
});
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
