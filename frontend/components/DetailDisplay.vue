<template>
  <BackButton />
  <NotificationBanner
    v-if="shouldShowBanner && resultData?.Name"
    :jurisdictionName="resultData.Name"
  />

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
    <div class="flex">
      <div v-if="loading" class="py-8 px-6">Loading...</div>
      <div
        v-else
        class="main-content prose -space-y-10 flex flex-col gap-12 py-8 px-6 w-full"
      >
        <!-- Loop over keyLabelPairs to display each key-value pair dynamically -->
        <div
          v-for="(item, index) in keyLabelPairs"
          :key="index"
          class="flex flex-col"
        >
          <!-- Check if it's the special 'Specialist' key -->
          <template v-if="item.key === 'Specialist'">
            <slot></slot>
          </template>
          <template v-else>
            <!-- Conditionally render the label -->
            <p
              v-if="item.key !== 'Legal provisions IDs'"
              class="label-key -mb-1"
            >
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
              <p
                :class="[
                  props.valueClassMap[item.key] || 'text-gray-800',
                  'text-sm leading-relaxed',
                ]"
              >
                {{ resultData?.[item.key] || 'N/A' }}
              </p>
            </template>
          </template>
        </div>
        <slot name="search-links"></slot>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { useRoute } from 'vue-router'

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

const route = useRoute()
const isJurisdictionPage = route.path.startsWith('/jurisdiction/')
const jurisdictionCode = route.params.id?.toLowerCase() // Extract ISO2 code
const coveredJurisdictions = ref([])
const shouldShowBanner = ref(false)

onMounted(async () => {
  try {
    const response = await fetch('/temp_answer_coverage.txt')
    const text = await response.text()

    // Convert the text file into an array of ISO2 codes
    coveredJurisdictions.value = text
      .split('\n')
      .map((code) => code.trim().toLowerCase())

    // Show banner only if jurisdictionCode is NOT in the covered list
    shouldShowBanner.value =
      isJurisdictionPage &&
      jurisdictionCode &&
      !coveredJurisdictions.value.includes(jurisdictionCode)
  } catch (error) {
    console.error('Failed to fetch covered jurisdictions:', error)
  }
})
</script>

<style scoped>
/* .main-content-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr)); /* 12-column layout */
/*column-gap: var(--gutter-width); /* Gutter space between columns */
/*padding: 32px; /* Optional padding to match the card's interior padding */
/*} */

/* .grid-item {
  grid-column: 1 / span 6; /* Start in the 1st column, span across 6 columns */
/* margin-bottom: 48px; /* Space between each key-value pair */
/*} */

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
  /* margin-top: -20px; */
}
</style>
