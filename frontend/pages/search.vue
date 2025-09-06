<template>
  <div>
    <!-- Show error message if there's an API error -->
    <div v-if="apiError" class="error-message">
      <p>
        We're sorry, but we encountered an error while processing your search.
        Please try again later.
      </p>
      <p class="error-details">{{ apiError }}</p>
    </div>
    <!-- Pass searchResults, totalMatches, and loading state -->
    <SearchResults
      v-else
      :data="{ tables: searchResults }"
      :total-matches="totalMatches"
      :loading="loading"
      v-model:filters="filter"
      :canLoadMore="searchResults.length < totalMatches"
      @load-more="loadMoreResults"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SearchResults from '@/components/search-results/SearchResults.vue'
import { useSearch } from '@/composables/useSearch'
import { useHead } from '#imports'

// Block a page from being indexed (https://nuxtseo.com/learn/controlling-crawlers#quick-implementation-guide)
useSeoMeta({
  robots: 'noindex, follow',
})

const route = useRoute()
const router = useRouter()
const searchQuery = ref(route.query.q || '') // Holds the search query from the URL
const searchResults = ref([]) // Stores search results to be displayed
const totalMatches = ref(0) // Save number of total matches to display at top of search results

const currentPage = ref(1)

// Persistent filter state
const filter = ref({
  jurisdiction: route.query.jurisdiction,
  theme: route.query.theme,
  type: route.query.type,
  sortBy: route.query.sortBy || 'relevance', // Add sortBy to filter state
})

const searchText = ref(route.query.q || '') // Initialize searchText from query

// Create search parameters for TanStack Query
const searchParams = computed(() => ({
  query: searchQuery.value,
  filters: filter.value,
  page: currentPage.value,
  pageSize: 10,
}))

// Use TanStack Query for search
const { data: searchData, isLoading, error } = useSearch(searchParams)

// Watch search data and update local state for pagination
watch(
  searchData,
  (newData) => {
    if (newData) {
      if (currentPage.value === 1) {
        // First page - replace results
        searchResults.value = newData.results
      } else {
        // Additional pages - append results
        searchResults.value = [...searchResults.value, ...newData.results]
      }
      totalMatches.value = newData.totalMatches
    }
  },
  { immediate: true }
)

// Create computed values for template
const loading = computed(() => isLoading.value)
const apiError = computed(() => error.value?.message || null)

// Keep searchText in sync with searchQuery
watch(searchQuery, (newQuery) => {
  searchText.value = newQuery || ''
})

// Set dynamic page title based on search string
watch(
  searchQuery,
  (newQuery) => {
    useHead({
      title:
        newQuery && newQuery.trim() ? `${newQuery} — CoLD` : 'Search — CoLD',
    })
  },
  { immediate: true }
)

// Watch for changes in filter and fetch results
watch(
  filter,
  (newFilters, oldFilters) => {
    if (JSON.stringify(newFilters) === JSON.stringify(oldFilters)) return // Avoid redundant updates

    // Reset pagination when filters change
    currentPage.value = 1
    searchResults.value = []

    const query = {
      ...route.query, // Retain existing query parameters
      jurisdiction: newFilters.jurisdiction,
      theme: newFilters.theme,
      type: newFilters.type,
    }

    // Remove `q` if searchText is empty
    if (!searchText.value.trim()) {
      delete query.q
    }

    // Remove undefined values from query
    Object.keys(query).forEach((key) => {
      if (query[key] === undefined) {
        delete query[key]
      }
    })

    // Update URL
    router.replace({
      name: 'search',
      query,
    })
  },
  { deep: true }
)

// Watch for URL query updates to sync the dropdowns
watch(
  () => route.query, // Watch the entire query object
  (newQuery) => {
    // Update searchQuery and filters based on the URL
    searchQuery.value = newQuery.q || ''

    // Reset pagination when URL changes
    currentPage.value = 1
    searchResults.value = []

    // Only update filters if they exist in the URL
    const newFilters = {}
    if (newQuery.jurisdiction) newFilters.jurisdiction = newQuery.jurisdiction
    if (newQuery.theme) newFilters.theme = newQuery.theme
    if (newQuery.type) newFilters.type = newQuery.type

    // Only update if the filters have actually changed
    if (JSON.stringify(newFilters) !== JSON.stringify(filter.value)) {
      filter.value = newFilters
    }
  },
  { deep: true, immediate: true } // Add immediate to handle initial URL
)

function loadMoreResults() {
  currentPage.value += 1
}

onMounted(() => {
  // Initialize search text from query
  searchText.value = route.query.q || ''
})
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
