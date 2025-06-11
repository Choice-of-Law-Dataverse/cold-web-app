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
import SearchResults from '~/components/search-results/SearchResults.vue'
import { useHead } from '#imports'

// Block a page from being indexed (https://nuxtseo.com/learn/controlling-crawlers#quick-implementation-guide)
useSeoMeta({
  robots: 'noindex, follow',
})

const route = useRoute()
const router = useRouter()
const searchQuery = ref(route.query.q || '') // Holds the search query from the URL
const searchResults = ref([]) // Stores search results to be displayed
const loading = ref(false) // Tracks the loading state for the API call
const totalMatches = ref(0) // Save number of total matches to display at top of search results
const apiError = ref(null) // Track API errors

const config = useRuntimeConfig()
const currentPage = ref(1)

// Persistent filter state
const filter = ref({
  jurisdiction: route.query.jurisdiction,
  theme: route.query.theme,
  type: route.query.type,
})

const searchText = ref(route.query.q || '') // Initialize searchText from query

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

    // Update URL and trigger search
    router
      .replace({
        name: 'search',
        query,
      })
      .then(() => {
        // Trigger a new search with the updated query and filters
        fetchSearchResults(searchText.value.trim(), newFilters)
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

    // Trigger a new search with the updated query and filters
    fetchSearchResults(newQuery.q || '', newFilters)
  },
  { deep: true, immediate: true } // Add immediate to handle initial URL
)

// Function to fetch search results from the API
async function fetchSearchResults(query, filters, append = false) {
  if (!append) {
    currentPage.value = 1
    searchResults.value = []
  }

  loading.value = true
  apiError.value = null // Reset any previous errors

  const requestBody = {
    search_string: query,
    page: currentPage.value,
    page_size: 10, // Hard code number of search results per page
    filters: [],
  }

  // Add "Jurisdictions" filter if defined
  if (filters.jurisdiction) {
    requestBody.filters.push({
      column: 'jurisdictions',
      values: filters.jurisdiction.split(','),
    })
  }

  // Add "Themes" filter if defined
  if (filters.theme) {
    requestBody.filters.push({
      column: 'themes',
      values: filters.theme.split(','),
    })
  }

  // Set up mapping: Filter options have different wording to table names
  const typeFilterMapping = {
    Questions: 'Answers',
    'Court Decisions': 'Court Decisions',
    'Legal Instruments': 'Domestic Instruments',
    'Domestic Instruments': 'Domestic Instruments',
    'Regional Instruments': 'Regional Instruments',
    'International Instruments': 'International Instruments',
    Literature: 'Literature',
  }

  // Add "Type" filter if defined
  if (filters.type) {
    requestBody.filters.push({
      column: 'tables',
      values: filters.type.split(',').map((type) => typeFilterMapping[type]),
    })
  }

  try {
    // Retrieve hostname safely (client only)
    const userHost =
      typeof window !== 'undefined' ? window.location.hostname : 'unknown'

    // Fetch user's IP address
    let userIp = 'Unknown'
    try {
      const ipResponse = await fetch('https://api.ipify.org?format=json')
      const ipData = await ipResponse.json()
      if (ipData.ip) {
        userIp = ipData.ip
      }
    } catch (error) {
      console.warn('Could not fetch IP address:', error)
    }

    // Add IP to request body safely
    requestBody.ip_address = userIp

    // Fetch detailed user info (browser, platform, etc.)
    const userInfo = await fetchUserInfo()
    const browserInfo = getBrowserInfo()

    // Add additional data to requestBody
    requestBody.ip_address = userIp
    requestBody.browser_info_navigator = browserInfo
    requestBody.browser_info_hint = userInfo || {}
    requestBody.hostname = userHost

    const response = await fetch(`${config.public.apiBaseUrl}/search/`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    })

    if (!response.ok) {
      // Handle 5xx errors
      if (response.status >= 500) {
        throw new Error(
          `Server error (${response.status}): ${response.statusText}`
        )
      }
      // Handle other errors
      throw new Error(`API error (${response.status}): ${response.statusText}`)
    }

    const data = await response.json()

    totalMatches.value = data.total_matches || 0

    if (append) {
      searchResults.value = [
        ...searchResults.value,
        ...Object.values(data.results),
      ]
    } else {
      searchResults.value = Object.values(data.results)
    }

    //searchResults.value = Object.values(data.results)
  } catch (error) {
    console.error('Error fetching search results:', error)
    apiError.value = error.message
    searchResults.value = []
    totalMatches.value = 0
  } finally {
    loading.value = false
  }
}

function loadMoreResults() {
  currentPage.value += 1
  fetchSearchResults(searchQuery.value, filter.value, true)
}

onMounted(() => {
  // Initialize search text from query
  searchText.value = route.query.q || ''

  // Fetch search results based on query and filters
  fetchSearchResults(searchQuery.value || '', filter.value)
})

// Set up functions to retrieve user data (https://developer.mozilla.org/en-US/docs/Web/API/Navigator)

// Browser Info
const getBrowserInfo = () => {
  if (typeof window === 'undefined') return {}
  const userAgent = navigator.userAgent // User agent string with browser and OS info
  const platform = navigator.platform // Operating system platform
  const language = navigator.language // Browser's language setting
  const screenWidth = window.screen.width // Screen width
  const screenHeight = window.screen.height // Screen height

  return {
    userAgent, // Provides browser and OS information in a single string
    platform, // Provides info about the operating system
    language, // Browser language setting
    screenWidth, // Screen width in pixels
    screenHeight, // Screen height in pixels
  }
}

// User Info
const fetchUserInfo = async () => {
  try {
    // Initial request to get the client hints (https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers#client_hints)
    await fetch(`${config.public.apiBaseUrl}/get_user_info`, {
      method: 'GET',
    })

    // After getting client hints from the browser, make a second request
    const response = await fetch(`${config.public.apiBaseUrl}/user_info`, {
      method: 'GET',
    })

    if (!response.ok) {
      throw new Error(`Failed to fetch user info: ${response.statusText}`)
    }

    const data = await response.json()
    return data // Return the user info data
  } catch (error) {
    console.error('Error fetching user info:', error)
    return null // Return null if there's an error
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
