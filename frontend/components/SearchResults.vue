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
              <div class="result-value">
                
                <template v-if="resultKey === 'Legal provision articles'">
                  <div v-if="resultData[resultKey]">
                    <!-- Render as link if there are legal provisions -->
                     <a href="#" @click.prevent="openLegalProvisionModal">
                      {{ resultData[resultKey] }}
                    </a>
                  </div>
                  <!-- Display fallback text if there are no legal provisions -->
                  <div v-else>No legal provision</div>
                  </template>

                <!-- Display other keys normally -->
                <template v-else>
                  {{ resultData[resultKey] }}
                </template>
              </div>
              <div style="margin-top: 2em;"></div>
            </div>
          </template>
          
          <template v-else>
          <!-- Display for Court decisions -->
          <div v-for="resultKey in courtDecisionKeys" :key="resultKey">
            <div class="result-key">{{ keyMap[resultKey] }}</div>
            <div class="result-value">
              <!-- Check if 'Choice of law issue' is empty and display default text -->
              <template v-if="resultKey === 'Choice of law issue'">
                {{ resultData[resultKey] || 'No choice of law issue' }}
              </template>
              <!-- Otherwise, render the value using createCollapsibleContent -->
              <template v-else>
                <span v-html="createCollapsibleContent(resultData[resultKey])"></span>
              </template>
            </div>
            <div style="margin-top: 2em;"></div>
          </div>
          <div><a href="#" @click.prevent="openCourtDecisionModal">Show more</a></div>
          <!-- <UButton label="Open CourtDecisionModal" @click="openModal" /> -->
        </template>
        
      </UCard>
      </div>
    </div>

    <!-- Pass isCourtDecisionModalOpen to CourtDecisionModal as isVisible -->
    <CourtDecisionModal v-if="isCourtDecisionModalOpen" :isVisible="isCourtDecisionModalOpen" @close="isCourtDecisionModalOpen = false" />

    <!-- Pass isLegalProvisionModalOpen to LegalProvisionModal as isVisible -->
    <LegalProvisionModal v-if="isLegalProvisionModalOpen" :isVisible="isLegalProvisionModalOpen" @close="isLegalProvisionModalOpen = false" />
  
  </UContainer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import CourtDecisionModal from '~/components/CourtDecisionModal.vue'

// Control the modal visibility
const isCourtDecisionModalOpen = ref(false)
const isLegalProvisionModalOpen = ref(false)

// Function to open the modal
function openCourtDecisionModal() {
  isCourtDecisionModalOpen.value = true
}

function openLegalProvisionModal() {
  isLegalProvisionModalOpen.value = true
}

// Define props and assign them to a variable
const props = defineProps({
  data: {
    type: Object,
    default: () => ({ tables: {} }) // Provide default value for data
  }
})

// Define the keys and their order for "Answers"
const answerKeys = ['Questions', 'Name (from Jurisdiction)', 'Answer', 'Legal provision articles']

// Define the keys and their order for "Court decisions"
const courtDecisionKeys = ['Case', 'Jurisdiction Names', 'Choice of law issue']

// Define a keyMap to rename the keys for display
const keyMap = {
  // Answers
  Answer: 'ANSWER',
  'Name (from Jurisdiction)': 'JURISDICTION',
  Questions: 'QUESTION',
  'Legal provision articles': 'LEGAL PROVISIONS',
  // Court Decisions
  Case: 'CASE TITLE',
  'Jurisdiction Names': 'JURISDICTION',
  'Choice of law issue': 'CHOICE OF LAW ISSUE'
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
  