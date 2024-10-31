<template>
  <div class="container">
    <div class="col-span-12">
      <BackButton />
      <UCard class="cold-ucard">
        <!-- Header section -->
        <template #header>
          <UCardHeader
            v-if="resultData"
            :resultData="resultData"
            :cardType="formattedSourceTable"
          />
        </template>

        <!-- Main content -->
        <div class="detail-content">
          <div v-if="loading">Loading...</div>
          <div v-else>
            <!-- Loop over keyLabelPairs to display each key-value pair dynamically -->
            <div v-for="(item, index) in keyLabelPairs" :key="index">
              <p class="result-key">{{ item.label }}</p>
              <p class="result-value">{{ resultData?.[item.key] || 'N/A' }}</p>
            </div>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps } from 'vue'
import BackButton from '~/components/BackButton.vue'
import UCardHeader from '~/components/UCardHeader.vue'

// Props for reusability across pages
const props = defineProps({
  loading: Boolean,
  resultData: Object,
  keyLabelPairs: Array,
  formattedSourceTable: {
    type: String,
    default: 'N/A',
  },
})

// Define `formattedSourceTable` locally to use in the header
const formattedSourceTable = computed(() => {
  const source_table = props.resultData?.source_table
  if (source_table === 'Court decisions') return 'Court decision'
  if (source_table === 'Answers') return 'Question'
  if (source_table === 'Legislation') return 'Legal Instrument'
  return source_table || ''
})

// Additional computed properties for other display elements
// const jurisdiction = computed( // () => props.resultData?.['Jurisdiction Names'] || null // )
// const formattedTheme = computed(() => props.resultData?.Themes || null)
</script>
