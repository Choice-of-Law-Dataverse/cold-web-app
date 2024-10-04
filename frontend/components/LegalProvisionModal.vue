<template>
  <div>
    <!-- Modal with custom width and centered positioning -->
    <UModal
      :modelValue="isVisible"
      :ui="{ width: 'w-full sm:max-w-4xl' }"
      prevent-close
      @close="emitClose"
    >
      <UCard
        :ui="{
          ring: '',
          divide: 'divide-y divide-gray-100 dark:divide-gray-800',
        }"
      >
        <template #header>
          <div class="flex items-center justify-between">
            <h3
              class="text-base font-semibold leading-6 text-gray-900 dark:text-white"
            >
              {{ data?.Name || '[Missing Name]' }}
              <!-- Display the Name value from data or a placeholder -->
            </h3>
            <UButton
              color="gray"
              variant="ghost"
              icon="i-heroicons-x-mark-20-solid"
              class="-my-1"
              @click="emitClose"
            />
          </div>
        </template>

        <!-- Modal Content -->

        <!-- Render dynamically generated key-value pairs -->
        <div v-for="(value, label) in keyValuePairs" :key="label">
          <p class="result-key">{{ label }}</p>
          <p class="result-value">{{ value }}</p>
        </div>

        <!-- Container for provision text and language selection -->
        <div class="provision-container">
          <p class="result-key">FULL TEXT OF THE PROVISION</p>
          <div class="right-container">
            <USelect
              size="2xs"
              variant="none"
              :options="['Original Language', 'English Translation']"
              v-model="selectedLanguage"
            />
          </div>
        </div>

        <!-- Conditionally display the full text of the provision -->
        <p class="result-value">{{ provisionText }}</p>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

// Define reactive variables
const selectedLanguage = ref('Original Language')

// Define props for the modal data
const props = defineProps<{
  isVisible: boolean
  data: Record<string, any>
}>()

// Fallback messages for missing data
const missingMessages = {
  'Jurisdiction name': '[Missing Jurisdiction]',
  Article: '[Missing Article]',
  'Full text of the provision (Original language)': '[Missing Text]',
  'Full text of the provision (English translation)': '[Missing Text]',
}

// Dynamically generate key-value pairs for jurisdiction and article
const keyValuePairs = computed(() => {
  return Object.entries(missingMessages).reduce(
    (acc, [column, missingText]) => {
      const key = column.toUpperCase().replace(/_/g, ' ')
      if (
        column !== 'Full text of the provision (Original language)' &&
        column !== 'Full text of the provision (English translation)'
      ) {
        acc[key] = props.data?.[column] || missingText
      }
      return acc
    },
    {}
  )
})

// Computed property to determine which provision text to display
const provisionText = computed(() => {
  return selectedLanguage.value === 'Original Language'
    ? props.data?.['Full text of the provision (Original language)'] ||
        missingMessages['Full text of the provision (Original language)']
    : props.data?.['Full text of the provision (English translation)'] ||
        missingMessages['Full text of the provision (English translation)']
})

// Emit the close event using arrow function
const emit = defineEmits(['close'])
const emitClose = () => emit('close')
</script>
