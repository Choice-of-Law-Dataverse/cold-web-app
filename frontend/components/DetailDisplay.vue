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
            :showOpenLink="false"
          />
        </template>

        <!-- Main content -->
        <div v-if="loading">Loading...</div>
        <div v-else class="main-content-grid">
          <!-- Loop over keyLabelPairs to display each key-value pair dynamically -->
          <div
            v-for="(item, index) in keyLabelPairs"
            :key="index"
            class="grid-item"
          >
            <p class="label-key">{{ item.label }}</p>
            <p :class="[props.valueClassMap[item.key] || 'default-class']">
              {{ resultData?.[item.key] || 'N/A' }}
            </p>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import BackButton from '~/components/BackButton.vue'
import UCardHeader from '~/components/UCardHeader.vue'

// Props for reusability across pages
const props = defineProps({
  loading: Boolean,
  resultData: Object,
  keyLabelPairs: Array,
  valueClassMap: Object,
  formattedSourceTable: String, // Receive the hard-coded value from [id].vue
})
</script>

<style scoped>
.main-content-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr)); /* 12-column layout */
  column-gap: var(--gutter-width); /* Gutter space between columns */
  padding: 32px; /* Optional padding to match the card's interior padding */
}

.grid-item {
  grid-column: 1 / span 6; /* Start in the 1st column, span across 6 columns */
  margin-bottom: 48px; /* Space between each key-value pair */
}
</style>
