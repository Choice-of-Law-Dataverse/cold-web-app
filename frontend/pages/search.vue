<template>
  <div>
    <!-- Pass searchResults, totalMatches, and loading state -->
    <SearchResults
      :data="{ tables: searchResults }"
      :total-matches="totalMatches"
      :loading="loading"
      v-model:filters="filter"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SearchResults from '../components/SearchResults.vue' // Adjust path if needed

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

const config = useRuntimeConfig()

// Persistent filter state
const filter = ref({
  jurisdiction: route.query.jurisdiction || 'All Jurisdictions',
  theme: route.query.theme || 'All Themes',
  type: route.query.type || 'All Types',
})

// Function to handle a new search
// const onSearchInput = (newQuery) => {
//   searchQuery.value = newQuery // Update the searchQuery state

//   // Update the URL query string with the new search term
//   router.push({
//     query: {
//       q: newQuery || undefined, // Only include 'q' if it's not empty
//       jurisdiction:
//         filter.value.jurisdiction !== 'All Jurisdictions'
//           ? filter.value.jurisdiction
//           : undefined,
//       theme:
//         filter.value.theme !== 'All Themes' ? filter.value.theme : undefined,
//       type: filter.value.type !== 'All Types' ? filter.value.type : undefined,
//     },
//   })

//   // Fetch new results with the updated search query and current filters
//   fetchSearchResults(newQuery || '', filter.value) // Allow empty search term
// }

// const hasActiveFilters = computed(() => {
//   return (
//     filter.value.jurisdiction !== 'All Jurisdictions' ||
//     filter.value.theme !== 'All Themes' ||
//     filter.value.type !== 'All Types'
//   )
// })

const searchText = ref(route.query.q || '') // Initialize searchText from query

// Keep searchText in sync with searchQuery
watch(searchQuery, (newQuery) => {
  searchText.value = newQuery || ''
})

// Watch for changes in filter and fetch results
watch(
  filter,
  (newFilters, oldFilters) => {
    if (JSON.stringify(newFilters) === JSON.stringify(oldFilters)) return // Avoid redundant updates

    const query = {
      ...route.query, // Retain existing query parameters
      jurisdiction:
        newFilters.jurisdiction !== 'All Jurisdictions'
          ? newFilters.jurisdiction
          : undefined,
      theme: newFilters.theme !== 'All Themes' ? newFilters.theme : undefined,
      type: newFilters.type !== 'All Types' ? newFilters.type : undefined,
    }

    // Remove `q` if searchText is empty
    if (!searchText.value.trim()) {
      delete query.q
    }

    router.replace({
      name: 'search',
      query,
    })
  },
  { deep: true }
)

watch(
  () => route.query, // Watch the entire query object
  (newQuery) => {
    // Update searchQuery and filters based on the URL
    searchQuery.value = newQuery.q || ''
    filter.value = {
      jurisdiction: newQuery.jurisdiction || 'All Jurisdictions',
      theme: newQuery.theme || 'All Themes',
      type: newQuery.type || 'All Types',
    }

    // Trigger a new search with the updated query and filters
    fetchSearchResults(searchQuery.value, filter.value)
  },
  { deep: true } // Deep watch to catch changes within the query object
)

// Function to fetch search results from the API
async function fetchSearchResults(query, filters) {
  loading.value = true
  searchResults.value = []

  const requestBody = {
    search_string: query,
    filters: [],
  }

  // Add "Jurisdictions" filter if not "All"
  if (filters.jurisdiction && filters.jurisdiction !== 'All Jurisdictions') {
    requestBody.filters.push({
      column: 'jurisdictions',
      values: [filters.jurisdiction],
    })
  }

  // Add "Themes" filter if not "All"
  if (filters.theme && filters.theme !== 'All Themes') {
    requestBody.filters.push({
      column: 'themes',
      values: [filters.theme],
    })
  }

  // Set up mapping: Filter options have different wording to table names
  const typeFilterMapping = {
    Questions: 'Answers',
    'Court Decisions': 'Court Decisions',
    'Legal Instruments': 'Domestic Instruments',
    //'Legal Instruments': 'International Legal Provisions',
    Literature: 'Literature',
  }

  // Add "Type" filter if not "All"
  if (filters.type && filters.type !== 'All Types') {
    requestBody.filters.push({
      column: 'tables',
      values: [typeFilterMapping[filters.type]],
    })
  }

  try {
    // Retrieve hostname
    const userHost = window.location.hostname

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

    const response = await fetch(
      `${config.public.apiBaseUrl}/search/`,
      //'http://localhost:5000/search/',
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      }
    )

    if (!response.ok) throw new Error('Failed to fetch results')

    const data = await response.json()

    totalMatches.value = data.total_matches || 0
    searchResults.value = Object.values(data.results)
  } catch (error) {
    console.error('Error fetching search results:', error)
  } finally {
    loading.value = false
  }
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

    const data = await response.json()
    return data // Return the user info data
  } catch (error) {
    console.error('Error fetching user info:', error)
    return null // Return null if there's an error
  }
}
</script>
