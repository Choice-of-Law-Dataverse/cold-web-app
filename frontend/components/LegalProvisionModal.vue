<template>
  <div>
    <!-- Button to trigger modal -->
    <!-- <UButton label="Open LegalProvisionModal" @click="isOpen = true" /> -->
    
    <!-- Modal with custom width and centered positioning -->
    <UModal :modelValue="isVisible" :ui="{ width: 'w-full sm:max-w-4xl' }" prevent-close @close="emitClose">
      <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
              {{ data?.Name || '[Missing Name]' }} <!-- Display the Name value from data or a placeholder -->
            </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1" @click="emitClose" />
          </div>
        </template>

        <!-- Modal Content -->  
          <p class="result-key">JURISDICTION</p>
          <p class="result-value">{{ data?.['Jurisdiction name'] || '[Missing Jurisdiction]' }}</p>
  
          <p class="result-key">ARTICLE</p>
          <p class="result-value">{{ data?.Article || '[Missing Article]' }}</p>
  
          <!-- Container with flexbox for aligned content -->
          <div class="provision-container">
            <p class="result-key">FULL TEXT OF THE PROVISION</p>
            <!-- Container for "Display:" and the select element -->
             <div class="right-container">
              <!-- <p class="display-label">Display:</p> -->
              <USelect
              size="2xs"
              variant="none"
              :options="['Original Language', 'English Translation']"
              model-value="Original Language"/>
            </div>
          </div>
          <p class="result-value">{{ data?.['Full text of the provision (Original language)'] || '[Missing Text]' }}</p>
      </UCard>
    </UModal>
  </div>
</template>

<style scoped>

.provision-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.right-container {
  display: flex; /* Keep the label and select in a row */
  align-items: center; /* Align them vertically */
}

.display-label {
  margin-right: 8px; /* Add space between "Display:" and the dropdown */
  text-align: right; /* Right align the "Display:" text */
  font-size: x-small;
  font-weight: bold;
}

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
import { defineProps, defineEmits } from 'vue';

const selected = ref(false)

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
