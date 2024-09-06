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
              [PLACEHOLDER] Swi-148 Art. 116
            </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1" @click="emitClose" />
          </div>
        </template>

        <!-- Modal Content -->  
          <p class="result-key">JURISDICTION</p>
          <p class="result-value">Switzerland</p>
  
          <p class="result-key">ARTICLE</p>
          <p class="result-value">Art. 116</p>
  
          <p class="result-key">FULL TEXT OF THE PROVISION</p>
          <p class="result-value">Far far away, behind the word mountains, far from the countries Vokalia and Consonantia, there live the blind texts. Separated they live in Bookmarksgrove right at the coast of the Semantics, a large language ocean. A small river named Duden flows by their place and supplies it with the necessary regelialia. It is a paradisematic country, in which roasted parts of sentences fly into your mouth. Even the all-powerful Pointing has no control about the blind texts it is an almost unorthographic life One day however a small line of blind text by the name of Lorem Ipsum decided to leave for the far World of Grammar. The Big Oxmox advised her not to do so, because there were thousands of bad Commas, wild Question Marks and devious Semikoli, but the Little Blind Text didn’t listen. She packed her seven versalia, put her initial into the belt and made herself on the way. When she reached the first hills of the Italic Mountains, she had a last view back on the skyline of her hometown Bookmarksgrove, the headline of Alphabet Village and the subline of her own road, the Line Lane. Pityful a rethoric question ran over her cheek, then
          </p>
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

import { defineEmits } from 'vue'

// Accept `isVisible` prop from the parent component
const props = defineProps({
  isVisible: Boolean
})

// Emit event for closing the modal
const emit = defineEmits(['close'])

// Function to emit the close event
function emitClose() {
  emit('close')
}

</script>
