<template>
  <div>
    <div v-if="searchQuery">
      <p v-if="loading" align="center">Loading…</p>

      <!-- Pass searchResults wrapped in `tables` to SearchResults.vue -->
      <SearchResults
        v-if="!loading && searchResults.length"
        :data="{ tables: searchResults }"
        :total-matches="totalMatches"
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

const route = useRoute() // Provides access to route parameters

// Function to fetch search results from the API
async function fetchSearchResults(query) {
  loading.value = true
  searchResults.value = []

  // Get browser and device info
  const browserInfo = getBrowserInfo()

  try {
    // Fetch the user's IP address using an external API
    const ipResponse = await fetch('https://api.ipify.org?format=json')
    const ipData = await ipResponse.json()
    const userIp = ipData.ip

    // Fetch detailed user info (browser, platform, etc.)
    const userInfo = await fetchUserInfo() // Call the fetchUserInfo function and await the result

    // Retrieve hostname to differentiate between alpha and beta users
    const userHost = window.location.hostname

    const requestBody = {
      // search_string: searchText.value,
      search_string: query,
      time: new Date().toISOString(), // Add timestamp as ISO string
      ip_address: userIp, // Add user's IP address
      browser_info_navigator: browserInfo, // Add browser and device info from navigator
      browser_info_hint: userInfo || {}, // Add user info (platform, version, etc.) from client hint
      hostname: userHost, // Include the current hostname
    }

    const response = await fetch(
      'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/full_text_search',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      }
    )

    if (!response.ok) throw new Error('Network response was not ok')
    const data = await response.json()

    // Extract total matches and results
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
