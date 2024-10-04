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
              {{ data?.Case || '[Missing Title]' }}
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
        <div v-if="props.isVisible" class="modal-content">
          <!-- Greyed out PDF download link -->
          <div class="icon-wrapper greyed-out">
            <UIcon name="i-material-symbols:file-open" />
          </div>
          <a class="result-value greyed-out">View original PDF<br /><br /></a>

          <!-- Reusable key-value rendering -->
          <div v-for="(value, label) in keyValuePairs" :key="label">
            <p class="result-key">{{ label }}</p>
            <p class="result-value">{{ value }}</p>
          </div>
        </div>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Define props without destructuring to maintain reactivity
const props = defineProps<{
  isVisible: boolean
  data: Record<string, any>
}>()

// Emit the close event
const emit = defineEmits(['close'])
const emitClose = () => emit('close')

// Define key-value pairs for rendering
const keyValuePairs = computed(() => ({
  JURISDICTION: props.data?.['Jurisdiction Names'] || '[Missing Jurisdiction]',
  ABSTRACT: props.data?.Abstract || '[No Abstract available]',
  'RELEVANT FACTS / SUMMARY OF THE CASE':
    props.data?.['Relevant facts / Summary of the case'] ||
    '[Missing Relevant Facts or Summary]',
  'RELEVANT RULES OF LAW INVOLVED':
    props.data?.['Relevant rules of law involved'] ||
    '[Missing Relevant Rules]',
  'CHOICE OF LAW ISSUE':
    props.data?.['Choice of law issue'] || '[Missing Choice of Law Issue]',
  "COURT'S POSITION":
    props.data?.["Court's position"] || "[Missing Court's Positions]",
  'TEXT OF THE RELEVANT LEGAL PROVISIONS':
    props.data?.['Text of the relevant legal provisions'] ||
    '[Missing Text of Relevant Legal Provisions]',
  QUOTE: props.data?.['Quote'] || '[Missing Quote]',
  'TRANSLATED EXCERPT':
    props.data?.['Translated excerpt'] || '[Missing Translated Excerpt]',
}))
</script>

<style scoped>
.greyed-out {
  color: grey;
  opacity: 0.5;
  cursor: not-allowed;
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
  margin-top: 1em;
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
