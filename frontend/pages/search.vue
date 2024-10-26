<template>
  <div>
    <h1>Search Results</h1>
    <div v-if="searchQuery">
      <!-- Display the search query -->
      <p>Results for: "{{ searchQuery }}"</p>

      <!-- Display results (replace with actual result rendering) -->
      <ul>
        <li v-for="result in searchResults" :key="result.id">
          {{ result.title }}
        </li>
      </ul>
    </div>
    <div v-else>
      <p>Please enter a search term in the navigation bar above.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const searchQuery = ref('') // Holds the search query from the URL
const searchResults = ref([]) // Stores search results to be displayed

const route = useRoute() // Provides access to route parameters

// Function to fetch search results based on query
function fetchSearchResults(query) {
  // Mock fetch function for demonstration purposes
  searchResults.value = [
    { id: 1, title: `Result for "${query}" 1` },
    { id: 2, title: `Result for "${query}" 2` },
    { id: 3, title: `Result for "${query}" 3` },
  ]
}

// Watch for changes in the query parameter and fetch new results
watch(
  () => route.query.q,
  (newQuery) => {
    if (newQuery) {
      searchQuery.value = newQuery
      fetchSearchResults(newQuery) // Fetch results based on the new query
    }
  }
)

// Fetch initial results if there's a query on first load
onMounted(() => {
  if (route.query.q) {
    searchQuery.value = route.query.q
    fetchSearchResults(searchQuery.value)
  }
})
</script>
