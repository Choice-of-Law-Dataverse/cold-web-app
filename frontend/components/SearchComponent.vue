<template>
  <div style="display: flex; flex-direction: column; align-items: center; width: 100%;">
    <!-- Input field and button aligned horizontally -->
    <div style="display: flex; justify-content: center; align-items: center; width: 100%; margin-bottom: 20px;">
      <UInput
        size="xl"
        v-model="searchText"
        @keyup.enter="performSearch"
        placeholder="Enter your search terms here"
        style="width: 40vw;"
      />
      <UButton
      :loading="loading"
      style="margin-left: 20px;"
      size="xl"
      @click="performSearch"
      >
      Search
    </UButton>
    </div>
    
    <!-- Display search results below the input and button -->
    <div>
      <SearchSuggestions v-if="showSuggestions" @suggestion-selected="updateSearchText" />
    </div>

    <!-- Display search results below the input and button -->
    <div>
      <SearchResults v-if="results" :data="results" />
    </div>
  </div>
</template>

<script setup lang="ts">

// Regular ref for non-persistent search text and results
const searchText = ref('') // Empty string as initial value
const results = ref(null) // Non-persistent search results
const showSuggestions = ref(true); // Add this to control the visibility of the SearchSuggestions component
const loading = ref(false); // Track the loading state

// Update search text when suggestion is clicked
const updateSearchText = (suggestion: string) => {
  searchText.value = suggestion;
  showSuggestions.value = false; // Hide suggestions when a suggestion is clicked
  performSearch(); // Trigger the search after updating the search text
}

const performSearch = async () => {
  showSuggestions.value = false; // Hide suggestions when the search button is clicked
  if (searchText.value.trim()) {
    loading.value = true; // Set loading to true when search starts
    try {
      const response = await fetch('https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/curated_search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ search_string: searchText.value }),
      })
      results.value = await response.json()
    } catch (error) {
      console.error('Error performing search:', error)
    } finally {
      loading.value = false; // Set loading to false when search completes
    }
  }
}
</script>
