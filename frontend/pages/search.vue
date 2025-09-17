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
      :canLoadMore="hasNextPage && !isFetchingNextPage"
      @load-more="loadMoreResults"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
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

const filter = ref({
  jurisdiction: route.query.jurisdiction,
  sortBy: route.query.sortBy || 'relevance', // Add sortBy to filter state
  theme: route.query.theme,
  type: route.query.type,
})

const searchText = ref(route.query.q || '') // Initialize searchText from query

const isInitialized = ref(false)

const searchParams = computed(() => {
  if (!isInitialized.value) {
    // Return empty params while not initialized to prevent queries
    return {
      filters: {},
      pageSize: 10,
      query: '',
      enabledOverride: false,
    }
  }

  return {
    filters: filter.value,
    pageSize: 10,
    query: searchQuery.value,
    enabledOverride: true,
  }
})


const {
  data: searchData,
  isLoading,
  error,
  fetchNextPage,
  hasNextPage,
  isFetchingNextPage,
} = useSearch(searchParams)

// Computed values for search results and total matches
const searchResults = computed(() => {
  if (!searchData.value?.pages) return []
  return searchData.value.pages.flatMap((page) => page.results)
})

const totalMatches = computed(() => {
  return searchData.value?.pages?.[0]?.totalMatches || 0
})

// Create computed values for template
const loading = computed(() => isLoading.value || isFetchingNextPage.value)
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

    // Only update filters if they exist in the URL
    const newFilters = {}
    if (newQuery.jurisdiction) newFilters.jurisdiction = newQuery.jurisdiction
    if (newQuery.theme) newFilters.theme = newQuery.theme
    if (newQuery.type) newFilters.type = newQuery.type

    // Only update if the filters have actually changed
    if (JSON.stringify(newFilters) !== JSON.stringify(filter.value)) {
      filter.value = newFilters
    }

    // Mark as initialized after first URL processing
    if (!isInitialized.value) {
      // Use nextTick to ensure all reactive updates are complete
      nextTick(() => {
        isInitialized.value = true
      })
    }
  },
  { deep: true, immediate: true } // Add immediate to handle initial URL
)

function loadMoreResults() {
  if (hasNextPage.value && !isFetchingNextPage.value) {
    fetchNextPage()
  }
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
