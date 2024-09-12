<template>
  <div>
    <!-- Button to trigger modal -->
    <!-- <UButton label="Open CourtDecisionsModal" @click="isOpen = true" /> -->
    
    <!-- Modal with custom width and centered positioning -->
    <UModal :modelValue="isVisible" :ui="{ width: 'w-full sm:max-w-4xl' }" prevent-close @close="emitClose">
      <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
              {{ data?.Case || '[Missing Title]' }} <!-- Display the Name value from data or a placeholder -->
            </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1" @click="emitClose" />
          </div>
        </template>

        <!-- Modal Content -->
        <div class="modal-content">
          <span class="icon-wrapper">
            <UIcon name="i-material-symbols:file-open" />
          </span>
          <a class="result-value">View original PDF<br><br></a>
          
          <p class="result-key">JURISDICTION</p>
          <p class="result-value">{{ data?.['Jurisdiction Names'] || '[Missing Jurisdiction]' }}</p>
  
          <p class="result-key">ABSTRACT</p>
          <p class="result-value">{{ data?.Abstract || '[No Abstract available]' }}</p>
  
          <p class="result-key">RELEVANT FACTS / SUMMARY OF THE CASE</p>
          <p class="result-value">{{ data?.['Relevant facts / Summary of the case'] || '[Missing Relevant Facts or Summary]' }}</p>

          <p class="result-key">RELEVANT RULES OF LAW INVOLVED</p>
          <p class="result-value">{{ data?.['Relevant rules of law involved'] || '[Missing Relevant Rules]' }}</p>

          <p class="result-key">CHOICE OF LAW ISSUE</p>
          <p class="result-value">{{ data?.['Choice of law issue'] || '[Missing Choice of Law Issue]' }}</p>

          <p class="result-key">COURT'S POSITION</p>
          <p class="result-value">{{ data?.["Court's position"] || "[Missing Court's Positions]" }}</p>

          <p class="result-key">TEXT OF THE RELEVANT LEGAL PROVISIONS</p>
          <p class="result-value">{{ data?.['Text of the relevant legal provisions'] || "[Missing Text of Relevant Legal Provisions]" }}</p>

          <p class="result-key">QUOTE</p>
          <p class="result-value">{{ data?.['Quote'] || "[Missing Quote]" }}</p>

          <p class="result-key">TRANSLATED EXCERPT</p>
          <p class="result-value">{{ data?.['Translated excerpt'] || "[Missing Translated Excerpt]" }}</p>
        </div>
      </UCard>
    </UModal>
  </div>
</template>

<style scoped>

.close-link {
  position: absolute;
  top: -20px;
  right: -10px;
  text-decoration: none;
  cursor: pointer;
  display: flex; /* Use flexbox to align icon and text horizontally */
  align-items: center; /* Align icon and text vertically */
}

.icon-wrapper {
    margin-right: 4px;
    margin-top: 5px;
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
    margin-bottom: 2em;
  }

  a {
    text-decoration: underline;
    text-underline-offset: 6px;
    text-decoration-thickness: 1px;
  }
  </style>

<script setup lang="ts">

// Accept `isVisible` prop from the parent component
const props = defineProps({
  isVisible: Boolean,
  data: Object  // Define the data prop to accept an object
})

// Emit event for closing the modal
const emit = defineEmits(['close'])

// Function to emit the close event
function emitClose() {
  emit('close')
}

</script>
  