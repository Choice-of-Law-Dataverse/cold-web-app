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
                
                <template v-if="resultKey === 'legal_provisions_articles_a'">
                  <div v-if="resultData[resultKey]">
                    <!-- Split the resultData[resultKey] by commas and loop through each item -->
                     <span v-for="(item, index) in resultData[resultKey].split(',')" :key="index" style="margin-right: 10px;">
                      <a href="#" @click.prevent="openLegalProvisionModal(item)">
                        {{ item.trim() }}
                      </a>
                    </span>
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
                {{ resultData[resultKey] || '[Missing Information]' }}
              </template>
              <!-- Otherwise, render the value using createCollapsibleContent -->
              <template v-else>
                <span v-html="createCollapsibleContent(resultData[resultKey])"></span>
              </template>
            </div>
            <div style="margin-top: 2em;"></div>
          </div>
          <div><a href="#" @click.prevent="openCourtDecisionModal(resultData)">Show more</a></div>
          <!-- <UButton label="Open CourtDecisionModal" @click="openModal" /> -->
        </template>
        
      </UCard>
      </div>
    </div>

    <!-- Pass isCourtDecisionModalOpen to CourtDecisionModal as isVisible -->
    <CourtDecisionModal v-if="isCourtDecisionModalOpen" :isVisible="isCourtDecisionModalOpen" :data="courtDecisionModalData" @close="isCourtDecisionModalOpen = false" />

    <!-- Pass isLegalProvisionModalOpen to LegalProvisionModal as isVisible -->
    <LegalProvisionModal v-if="isLegalProvisionModalOpen" :isVisible="isLegalProvisionModalOpen" :data="legalProvisionModalData" @close="isLegalProvisionModalOpen = false" />
  
  </UContainer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import CourtDecisionModal from '~/components/CourtDecisionModal.vue'
import LegalProvisionModal from '~/components/LegalProvisionModal.vue'


// Control the modal visibility
const isCourtDecisionModalOpen = ref(false)
const isLegalProvisionModalOpen = ref(false)

// Linking modals to dynamic data
const resultKey = ref('relevant_provisions_a');
const resultData = ref({});  // Placeholder for your actual data

// This will store the response data to be passed to the modal
const legalProvisionModalData = ref(null);
const courtDecisionModalData = ref(null);


// Function to open the modal
async function openCourtDecisionModal(courtDecision) {
  // Create the JSON object
  const decisionJson = {
    table: "Court decisions",
    id: courtDecision.id.trim()  // Trim in case of extra spaces
  };

  // console.log(decisionJson)
  
  try {
  // Make a POST request to your desired URL (replace 'your-url' with the actual URL)
  const response = await fetch('https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/curated_search/details', {
    method: 'POST',  // Use POST to send data
    headers: {
      'Content-Type': 'application/json',  // Specify JSON content
    },
    body: JSON.stringify(decisionJson)  // Send the provisionJson as the request body
  });

  // Check if the response is OK (status 200-299)
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  // Parse the JSON response from the server
  const responseData = await response.json();

  // Log the response data to the console (or handle it however you need)
  // console.log('Response data:', responseData);

  courtDecisionModalData.value = responseData;  // Store the response data in the modalData ref

  // Open the modal
  isCourtDecisionModalOpen.value = true

} catch (error) {
  // Handle any errors that occur during the fetch
  console.error('Error fetching data:', error);
}
}

async function openLegalProvisionModal(legalProvision) {
  // Create the JSON object
  const provisionJson = {
    table: "Legal provisions",
    id: legalProvision.trim()  // Trim in case of extra spaces
  };

  // console.log(provisionJson);  // Log the object to confirm it's correct

try {
  // Make a POST request to your desired URL (replace 'your-url' with the actual URL)
  const response = await fetch('https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/curated_search/details', {
    method: 'POST',  // Use POST to send data
    headers: {
      'Content-Type': 'application/json',  // Specify JSON content
    },
    body: JSON.stringify(provisionJson)  // Send the provisionJson as the request body
  });

  // Check if the response is OK (status 200-299)
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  // Parse the JSON response from the server
  const responseData = await response.json();

  // Log the response data to the console (or handle it however you need)
  // console.log('Response data:', responseData);

  legalProvisionModalData.value = responseData;  // Store the response data in the modalData ref

  // Open the modal
  isLegalProvisionModalOpen.value = true;

} catch (error) {
  // Handle any errors that occur during the fetch
  console.error('Error fetching data:', error);
}
}

// Define props and assign them to a variable
const props = defineProps({
  data: {
    type: Object,
    default: () => ({ tables: {} }) // Provide default value for data
  }
})

// Define the keys and their order for "Answers"
const answerKeys = ['questions', 'name_from_jurisdiction_a', 'answer_a', 'legal_provisions_articles_a']

// Define the keys and their order for "Court decisions"
const courtDecisionKeys = ['case_cd', 'jurisdiction_names_cd', 'choice_of_law_issue_cd']

// Define a keyMap to rename the keys for display
const keyMap = {
  // Answers
  'answer_a': 'ANSWER',
  'name_from_jurisdiction_a': 'JURISDICTION',
  'questions': 'QUESTION',
  'legal_provisions_articles_a': 'LEGAL PROVISIONS',
  // Court Decisions
  'case_cd': 'CASE TITLE',
  'jurisdiction_names_cd': 'JURISDICTION',
  'choice_of_law_issue_cd': 'CHOICE OF LAW ISSUE'
}

// Gather all results
const allResults = computed(() => {
  return Object.values(props.data.results);
})

// Utility functions

function isAnswer(resultData) {
  // Check if 'source_table' key exists and if its value is "Answers"
  return resultData.source_table === 'Answers';
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
  