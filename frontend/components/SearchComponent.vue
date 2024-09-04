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
        style="margin-left: 20px;"
        size="xl"
        @click="performSearch"
      >
        Search
      </UButton>
    </div>
    
    <!-- Display search results below the input and button -->
    <div>
      <SearchResults v-if="results" :data="results" :isSemanticSearch="isSemanticSearch" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useState } from '#imports'  // Correct import for Nuxt 3

// Persist the search text across page navigations
const searchText = useState('searchText', () => '') // Empty string as initial value
const results = useState('results', () => null) // Persistent search results
const isSemanticSearch = useState('isSemanticSearch', () => false) // Persistent search type

const performSearch = async () => {
  if (searchText.value.trim()) {
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
    }
  }
}
</script>
