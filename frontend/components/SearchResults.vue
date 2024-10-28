<template>
  <UContainer
    style="
      margin-top: 50px;
      width: 80%;
      max-width: 1200px;
      margin-left: auto;
      margin-right: auto;
    "
  >
    <p style="text-align: right; padding-bottom: 50px">
      {{ props.totalMatches }} Results
    </p>
    <div class="results-grid">
      <!-- <h2>Search Results</h2> -->
      <div
        v-for="(resultData, key) in allResults"
        :key="key"
        class="result-item"
      >
        <UCard>
          <!-- Conditional rendering based on the type of search result -->

          <!-- Display for Answers -->
          <template v-if="isAnswer(resultData)">
            <div v-for="(resultKey, index) in answerKeys" :key="resultKey">
              <div class="result-key">{{ keyMap[resultKey] }}</div>
              <div
                :class="[
                  'result-value',
                  { 'no-margin': index === answerKeys.length - 1 },
                ]"
              >
                <template v-if="resultKey === 'Legal provision articles'">
                  <div v-if="resultData[resultKey]">
                    <span
                      v-for="(item, index) in resultData[resultKey].split(',')"
                      :key="index"
                      style="margin-right: 10px"
                    >
                      <a
                        href="#"
                        @click.prevent="openLegalProvisionModal(item)"
                      >
                        {{ item.trim() }}
                      </a>
                    </span>
                  </div>
                  <div v-else>No legal provision</div>
                  <br />
                  <NuxtLink :to="`/question/${resultData.id}`">Open</NuxtLink>
                </template>
                <template v-else>
                  {{ resultData[resultKey] }}
                </template>
              </div>
            </div>
          </template>

          <!-- Display for Court decisions -->
          <template v-else-if="isCourtDecision(resultData)">
            <div v-for="resultKey in courtDecisionKeys" :key="resultKey">
              <div class="result-key">{{ keyMap[resultKey] }}</div>
              <div class="result-value">
                <template v-if="resultKey === 'Choice of law issue'">
                  {{ resultData[resultKey] || '[Missing Information]' }}
                </template>
                <template v-else>
                  <span>{{ resultData[resultKey] }}</span>
                </template>
              </div>
            </div>
            <div>
              <NuxtLink :to="`/court-decision/${resultData.id}`">Open</NuxtLink>
            </div>
          </template>

          <!-- Display for Legislation -->
          <template v-else-if="isLegislation(resultData)">
            <div
              v-for="legislationKey in legislationKeys"
              :key="legislationKey"
            >
              <div class="result-key">{{ keyMap[legislationKey] }}</div>
              <div class="result-value">
                {{ resultData[legislationKey] || '[Missing Information]' }}
              </div>
            </div>
            <div>
              <NuxtLink :to="`/legal-instrument/${resultData.id}`"
                >Open</NuxtLink
              >
            </div>
          </template>

          <!-- Default case if no source_table matches -->
          <template v-else>
            <div>No matching source found</div>
          </template>
        </UCard>
      </div>
    </div>

    <!-- Pass isCourtDecisionModalOpen to CourtDecisionModal as isVisible -->
    <CourtDecisionModal
      v-if="isCourtDecisionModalOpen"
      :isVisible="isCourtDecisionModalOpen"
      :data="courtDecisionModalData"
      @close="isCourtDecisionModalOpen = false"
    />

    <!-- Pass isLegalProvisionModalOpen to LegalProvisionModal as isVisible -->
    <LegalProvisionModal
      v-if="isLegalProvisionModalOpen"
      :isVisible="isLegalProvisionModalOpen"
      :data="legalProvisionModalData"
      @close="isLegalProvisionModalOpen = false"
    />
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
const resultKey = ref('Relevant provisions')
const resultData = ref({}) // Placeholder for your actual data

// This will store the response data to be passed to the modal
const legalProvisionModalData = ref(null)
const courtDecisionModalData = ref(null)

// Generic function to open a modal for either court decisions or legal provisions
async function openModal(type, id, modalDataRef, isModalOpenRef) {
  // Create the JSON object dynamically based on the type
  const jsonPayload = {
    table: type, // Either 'Court decisions' or 'Legal provisions'
    id: id.trim(), // Trim in case of extra spaces
  }

  try {
    const response = await fetch(
      'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/curated_search/details',
      {
        method: 'POST', // Use POST to send data
        headers: {
          'Content-Type': 'application/json', // Specify JSON content
        },
        body: JSON.stringify(jsonPayload), // Send the jsonPayload as the request body
      }
    )

    // Check if the response is OK (status 200-299)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    // Parse the JSON response from the server
    const responseData = await response.json()

    // Store the response data in the appropriate modalData ref
    modalDataRef.value = responseData

    // Open the modal by setting the isModalOpen ref to true
    isModalOpenRef.value = true
  } catch (error) {
    // Handle any errors that occur during the fetch
    console.error('Error fetching data:', error)
  }
}

// Function to open the court decision modal
async function openCourtDecisionModal(courtDecision) {
  await openModal(
    'Court decisions', // Type of data
    courtDecision.id, // ID for the court decision
    courtDecisionModalData, // Ref to hold the response data
    isCourtDecisionModalOpen // Ref to track the modal's open state
  )
}

// Function to open the legal provision modal
async function openLegalProvisionModal(legalProvision) {
  await openModal(
    'Legal provisions', // Type of data
    legalProvision, // ID for the legal provision
    legalProvisionModalData, // Ref to hold the response data
    isLegalProvisionModalOpen // Ref to track the modal's open state
  )
}

// Define props and assign them to a variable
const props = defineProps({
  data: {
    type: Object,
    default: () => ({ tables: {} }), // Provide default value for data
  },
  totalMatches: {
    type: Number,
    default: 0,
  },
})

// Define the keys and their order for "Answers"
const answerKeys = [
  'Questions',
  'Name (from Jurisdiction)',
  'Answer',
  'Legal provision articles',
]

// Define the keys and their order for "Court decisions"
const courtDecisionKeys = ['Case', 'Jurisdiction Names', 'Choice of law issue']

// Define the keys and their order for "Court decisions"
const legislationKeys = ['Title (in English)', 'Jurisdiction name']

// Define a keyMap to rename the keys for display
const keyMap = {
  // Answers
  Answer: 'ANSWER',
  'Name (from Jurisdiction)': 'JURISDICTION',
  Questions: 'QUESTION',
  'Legal provision articles': 'SOURCE',
  // Court Decisions
  Case: 'CASE TITLE',
  'Jurisdiction Names': 'JURISDICTION',
  'Choice of law issue': 'CHOICE OF LAW ISSUE',
  // Legislations
  'Title (in English)': 'TITLE',
  'Jurisdiction name': 'JURISDICTION',
}

// Gather all results
const allResults = computed(() => {
  return Object.values(props.data.tables)
})

// Utility functions

function isAnswer(resultData) {
  return resultData.source_table === 'Answers'
}

function isCourtDecision(resultData) {
  return resultData.source_table === 'Court decisions'
}

function isLegislation(resultData) {
  return resultData.source_table === 'Legislation'
}
</script>
