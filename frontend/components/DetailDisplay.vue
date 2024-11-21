<template>
  <div class="container">
    <div class="col-span-12">
      <BackButton />
      <UCard class="cold-ucard">
        <!-- Header section -->
        <template #header v-if="showHeader">
          <UCardHeader
            v-if="resultData"
            :resultData="resultData"
            :cardType="formattedSourceTable"
            :showOpenLink="false"
          />
        </template>

        <!-- Main content -->
        <div v-if="loading" class="main-content-grid">Loading...</div>
        <div v-else class="main-content-grid">
          <!-- Loop over keyLabelPairs to display each key-value pair dynamically -->
          <div
            v-for="(item, index) in keyLabelPairs"
            :key="index"
            class="grid-item"
          >
            <!-- Conditionally render the label -->
            <p v-if="item.key !== 'Legal provisions IDs'" class="label-key">
              {{ item.label }}
            </p>
            <!-- Dynamic slot with kebab-case conversion -->
            <template
              v-if="$slots[item.key.replace(/ /g, '-').toLowerCase()]"
              :slot="item.key.replace(/ /g, '-').toLowerCase()"
            >
              <slot
                :name="item.key.replace(/ /g, '-').toLowerCase()"
                :value="resultData?.[item.key]"
              />
            </template>
            <template v-else>
              <p :class="[props.valueClassMap[item.key] || 'default-class']">
                {{ resultData?.[item.key] || 'N/A' }}
              </p>
            </template>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup>
import BackButton from '~/components/BackButton.vue'
import UCardHeader from '~/components/UCardHeader.vue'

// Props for reusability across pages
const props = defineProps({
  loading: Boolean,
  resultData: Object,
  keyLabelPairs: Array,
  valueClassMap: Object,
  formattedSourceTable: String, // Receive the hard-coded value from [id].vue
  showHeader: {
    type: Boolean,
    default: true, // Default to true so headers are shown unless explicitly disabled
  },
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

.cold-ucard {
  margin-bottom: 120px;
}

.cold-ucard ::v-deep(.px-4) {
  padding-left: 0 !important;
  padding-right: 0 !important;
}

.cold-ucard ::v-deep(.py-5) {
  padding-top: 16px !important;
  padding-bottom: 18px !important;
}

.cold-ucard ::v-deep(.sm\:px-6) {
  padding-left: 16px !important;
  padding-right: 16px !important;
}

.label-key {
  @extend .label;
  padding: 0;
  margin-top: -20px;
}
</style>
