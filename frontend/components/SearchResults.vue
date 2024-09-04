<template>
  <UContainer style="margin-top: 50px; width: 80%; max-width: 1200px; margin-left: auto; margin-right: auto;">
    <div class="results-grid">
      <div v-for="(resultData, key) in allResults" :key="key" class="result-item">
        <UCard>
          <div v-for="(value, resultKey) in resultData" :key="resultKey">
            <div class="result-key">{{ formatTitle(resultKey) }}</div>
            <div class="result-value" v-html="createCollapsibleContent(value)"></div>
          </div>
        </UCard>
      </div>
    </div>
  </UContainer>
</template>
  
<script setup lang="ts">
import { ref, computed } from 'vue'

// Define props and assign them to a variable
const props = defineProps<{
  data: {
    tables: Record<string, {
      matches: number;
      results: Record<string, any>;
    }>
  }
}>()

// Computed property to gather all results from all tables
const allResults = computed(() => {
  let results = [];
  for (const table in props.data.tables) {
    results = results.concat(Object.values(props.data.tables[table].results));
  }
  return results;
})

// Utility functions
function formatTitle(key: string): string {
  // Your existing logic for formatting titles
  return key.replace(/_/g, ' ').toUpperCase();
}

function createCollapsibleContent(value: string): string {
  // Your existing logic for creating collapsible content
  return value; // Simplified for example purposes, replace with your actual logic
}
</script>


  
  <style scoped>
  /* Container style is defined inline in the template */
  
  .results-grid {
    /* display: grid; */
    /* grid-template-columns: repeat(auto-fill, minmax(600px, 1fr)); Set a larger minimum width */
    /* gap: 20px; Maintain the gap between cards */
}
  
  .result-item {
    margin-bottom: 1rem;
  }
  
  .result-key {
    font-weight: bold;
  }
  
  /* Adding styles to ensure text wrapping */
  .result-value {
    word-wrap: break-word; /* Allows breaking within words if necessary */
    word-break: break-word; /* Breaks words that are too long */
    white-space: pre-wrap; /* Preserves whitespace and line breaks, but also allows wrapping */
  }
  </style>
  