<template>
  <div>
    <div v-if="searchQuery">
      <p v-if="loading" align="center">Loading…</p>

      <!-- Pass searchResults wrapped in `tables` to SearchResults.vue -->
      <SearchResults
        v-if="!loading && searchResults.length"
        :data="{ tables: searchResults }"
        :total-matches="totalMatches"
        v-model:filter="filter"
        @filter-updated="onFilterUpdated"
      />

      <p v-if="!loading && !searchResults.length">No results found.</p>
    </div>
    <div v-else>
      <p align="center">
        Please enter a search term in the navigation bar above.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import SearchResults from '../components/SearchResults.vue' // Adjust path if needed

const searchQuery = ref('') // Holds the search query from the URL
const searchResults = ref([]) // Stores search results to be displayed
const loading = ref(false) // Tracks the loading state for the API call
const totalMatches = ref(0) // Save number of total matches to display at top of search results
const filter = ref('All Types')
const route = useRoute() // Provides access to route parameters

// Handle filter updates
const onFilterUpdated = (newFilter) => {
  filter.value = newFilter
  fetchSearchResults(searchQuery.value, filter.value)
}

// Function to fetch search results from the API
async function fetchSearchResults(query, selectedFilter = 'All Types') {
  loading.value = true
  searchResults.value = []

  const filters =
    selectedFilter === 'Question'
      ? [{ column: 'tables', values: ['Answers'] }]
      : []

  const requestBody = {
    search_string: query,
    filters, // Add filters dynamically
    time: new Date().toISOString(),
  }

  try {
    const response = await fetch(
      'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/full_text_search',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      }
    )

    const data = await response.json()
    totalMatches.value = data.total_matches || 0
    searchResults.value = Object.values(data.results)
  } catch (error) {
    console.error('Error fetching search results:', error)
  } finally {
    loading.value = false
  }
}

watch(
  () => route.query.q,
  (newQuery) => {
    if (newQuery) {
      searchQuery.value = newQuery
      fetchSearchResults(newQuery)
    }
  }
)

onMounted(() => {
  if (route.query.q) {
    searchQuery.value = route.query.q
    fetchSearchResults(searchQuery.value)
  }
})

// Set up functions to retrieve user data (https://developer.mozilla.org/en-US/docs/Web/API/Navigator)

// Browser Info
const getBrowserInfo = () => {
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
    await fetch(
      'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/get_user_info',
      {
        method: 'GET',
      }
    )

    // After getting client hints from the browser, make a second request
    const response = await fetch(
      'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/user_info',
      {
        method: 'GET',
      }
    )

    const data = await response.json()
    return data // Return the user info data
  } catch (error) {
    console.error('Error fetching user info:', error)
    return null // Return null if there's an error
  }
}
</script>
