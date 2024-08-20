<template>
    <UContainer style="margin-top: 50px; width: 80%; max-width: 1200px; margin-left: auto; margin-right: auto;">
      <p>Total Matches: {{ data.total_matches }}</p>
  
      <template v-if="isSemanticSearch">
        <div class="results-grid">
          <div v-for="(result, index) in data.results" :key="index" class="result-item">
            <UCard>
              <div v-for="(value, key) in result" :key="key">
                <div class="result-key">{{ formatTitle(key) }}</div>
                <div class="result-value" v-html="createCollapsibleContent(value)"></div>
              </div>
            </UCard>
          </div>
        </div>
      </template>
  
      <template v-else>
        <div class="results-grid">
          <div v-for="(tableData, table) in data.tables" :key="table">
            <h2>{{ formatTitle(table) }} (Matches: {{ tableData.matches }})</h2>
            <div v-for="(resultData, key) in tableData.results" :key="key" class="result-item">
              <UCard>
                <div v-for="(value, resultKey) in resultData" :key="resultKey">
                  <div class="result-key">{{ formatTitle(resultKey) }}</div>
                  <div class="result-value" v-html="createCollapsibleContent(value)"></div>
                </div>
              </UCard>
            </div>
          </div>
        </div>
      </template>
    </UContainer>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue'
  
  // Props
  defineProps({
    data: Object,
    isSemanticSearch: Boolean,
  })
  
  // Utility functions
  function formatTitle(key) {
    // Your existing logic for formatting titles
    return key.replace(/_/g, ' ').toUpperCase();
  }
  
  function createCollapsibleContent(value) {
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
  