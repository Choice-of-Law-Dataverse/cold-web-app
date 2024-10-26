<template>
  <div>
    <!-- <h1>Search Results</h1> -->
    <div v-if="searchQuery">
      <!-- <p>Results for: "{{ searchQuery }}"</p> -->

      <p v-if="loading">Loading...</p>

      <!-- Pass searchResults wrapped in `tables` to SearchResults.vue -->
      <SearchResults
        v-if="!loading && searchResults.length"
        :data="{ tables: searchResults }"
      />

      <p v-if="!loading && !searchResults.length">No results found.</p>
    </div>
    <div v-else>
      <p>Please enter a search term in the navigation bar above.</p>
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

const route = useRoute() // Provides access to route parameters

// Function to fetch search results from the API
async function fetchSearchResults(query) {
  loading.value = true
  searchResults.value = []

  try {
    const requestBody = { search_string: query }
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
</script>
