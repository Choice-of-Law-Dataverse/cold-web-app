<template>
  <div>
    <!-- Button to trigger modal -->
    <UButton label="Open LegalProvisionModal" @click="isOpen = true" />
    
    <!-- Modal with custom width and centered positioning -->
    <UModal v-model="isOpen" :ui="{ width: 'w-full sm:max-w-4xl' }" prevent-close>
      <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
              Swi-148 Art. 116
            </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1" @click="isOpen = false" />
          </div>
        </template>

        <!-- Modal Content -->  
          <p class="result-key">JURISDICTION</p>
          <p class="result-value">Switzerland</p>
  
          <p class="result-key">ARTICLE</p>
          <p class="result-value">Art. 116</p>
  
          <p class="result-key">FULL TEXT OF THE PROVISION</p>
          <p class="result-value">
            1 Contracts are governed by the law chosen by the parties.2 The choice of law must be express or result with certainty from the provisions of the contract or from the circumstances; apart from that, it is governed by the chosen law.3 The choice of law may be made or changed at any time. If a choice of law is made after the conclusion of the contract, it has retroactive effect as of the time of conclusion of the contract. The rights of third parties are reserved.
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
const isOpen = ref(false)
</script>
  