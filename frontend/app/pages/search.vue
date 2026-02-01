<template>
  <div>
    <div v-if="apiError" class="error-message">
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

<script setup>
import { ref, onMounted, watch, computed, nextTick } from "vue";
import { useRoute } from "vue-router";
import SearchResults from "@/components/search-results/SearchResults.vue";
import { useSearch } from "@/composables/useSearch";
import { useHead, useSeoMeta } from "#imports";

useSeoMeta({
  robots: "noindex, follow",
});

const route = useRoute();
const searchQuery = ref(route.query.q || "");

const filter = ref({
  jurisdiction: route.query.jurisdiction,
  sortBy: route.query.sortBy || "relevance",
  theme: route.query.theme,
  type: route.query.type,
});

const searchText = ref(route.query.q || "");

const isInitialized = ref(false);

const searchParams = computed(() => {
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
  searchText.value = newQuery || "";
});

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

watch(
  filter,
  (newFilters, oldFilters) => {
    if (route.name !== "search") return;
    if (JSON.stringify(newFilters) === JSON.stringify(oldFilters)) return;

    const query = {
      ...route.query,
      jurisdiction: newFilters.jurisdiction,
      sortBy: newFilters.sortBy,
      theme: newFilters.theme,
      type: newFilters.type,
    };

    if (!searchText.value.trim()) {
      delete query.q;
    }

    const cleanedQuery = Object.fromEntries(
      Object.entries(query).filter(([_, value]) => value !== undefined),
    );

    // Use navigateTo with replace option as recommended by Nuxt docs
    navigateTo({ path: "/search", query: cleanedQuery }, { replace: true });
  },
  { deep: true },
);

watch(
  () => route.query,
  (newQuery) => {
    // Don't update state if navigating away from search page
    if (route.name !== "search") return;

    searchQuery.value = newQuery.q || "";

    const newFilters = {};
    if (newQuery.jurisdiction) newFilters.jurisdiction = newQuery.jurisdiction;
    if (newQuery.sortBy) newFilters.sortBy = newQuery.sortBy;
    if (newQuery.theme) newFilters.theme = newQuery.theme;
    if (newQuery.type) newFilters.type = newQuery.type;

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
  searchText.value = route.query.q || "";
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
