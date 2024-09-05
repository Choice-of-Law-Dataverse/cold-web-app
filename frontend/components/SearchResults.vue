<template>
  <UContainer style="margin-top: 50px; width: 80%; max-width: 1200px; margin-left: auto; margin-right: auto;">
    <div class="results-grid">
      <div v-for="(resultData, key) in allResults" :key="key" class="result-item">
        <UCard>
          <!-- Conditional rendering based on the type of search result -->
          <template v-if="isAnswer(resultData)">
            <!-- Display for Answers -->
            <div v-for="resultKey in answerKeys" :key="resultKey">
              <div class="result-key">{{ keyMap[resultKey] }}</div>
              <div class="result-value" v-html="createCollapsibleContent(resultData[resultKey])"></div>
              <div style="margin-top: 2em;"></div>
            </div>
          </template>
          <template v-else>
            <!-- Display for Court decisions -->
            <div v-for="resultKey in courtDecisionKeys" :key="resultKey">
              <div class="result-key">{{ keyMap[resultKey] }}</div>
              <div class="result-value" v-html="createCollapsibleContent(resultData[resultKey])"></div>
              <div style="margin-top: 2em;"></div>
              <div><a href="/">Show more</a></div>
            </div>
          </template>
        </UCard>
      </div>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// Define props and assign them to a variable
const props = defineProps({
  data: {
    type: Object,
    default: () => ({ tables: {} }) // Provide default value for data
  }
})

// Define the keys and their order for "Answers"
const answerKeys = ['Questions', 'Name (from Jurisdiction)', 'Answer']

// Define the keys and their order for "Court decisions"
const courtDecisionKeys = ['Case']

// Define a keyMap to rename the keys for display
const keyMap = {
  Answer: 'ANSWER',
  'Name (from Jurisdiction)': 'JURISDICTION',
  Questions: 'QUESTION',
  Case: 'CASE TITLE'
}

// Computed property to gather all results from all tables
const allResults = computed(() => {
  let results = [];
  for (const table in props.data.tables) {
    results = results.concat(Object.values(props.data.tables[table].results));
  }
  return results;
})

// Utility functions

// Function to detect if the resultData is for an "Answer"
function isAnswer(resultData) {
  // Assuming that "Answer" is a key that exists only in "Answers" type results
  return 'Answer' in resultData;
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
    font-size: x-small;
    font-weight: bold;
  }
  
  /* Adding styles to ensure text wrapping */
  .result-value {
    word-wrap: break-word; /* Allows breaking within words if necessary */
    word-break: break-word; /* Breaks words that are too long */
    white-space: pre-wrap; /* Preserves whitespace and line breaks, but also allows wrapping */
  }

  a {
    text-decoration: underline;
    text-underline-offset: 6px;
    text-decoration-thickness: 1px;
  }
  </style>
  