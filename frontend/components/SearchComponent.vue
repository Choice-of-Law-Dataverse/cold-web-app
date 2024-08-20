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
import { ref } from 'vue'
import axios from 'axios'
import SearchResults from '~/components/SearchResults.vue'

const searchText = ref('')
const results = ref(null)
const isSemanticSearch = ref(false) // Set this based on your search type logic

const performSearch = async () => {
  if (searchText.value.trim()) {
    try {
      const response = await axios.post('http://127.0.0.1:5000/search', {
        search_string: searchText.value,
        use_semantic_search: isSemanticSearch.value,
      })
      results.value = response.data
    } catch (error) {
      console.error('Error performing search:', error)
    }
  }
}

</script>
