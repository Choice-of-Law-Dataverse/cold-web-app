<template>
  <div class="header-container">
    <!-- Left side of the header -->
    <div>
      <!-- Display 'Name (from Jurisdiction)' or alternatives -->
      <span
        v-for="(jurisdictionString, index) in formattedJurisdiction"
        :key="index"
        class="label-jurisdiction"
      >
        {{ jurisdictionString }}
      </span>

      <!-- Display 'source_table' -->
      <span v-if="adjustedSourceTable" :class="['label', labelColorClass]">
        {{ adjustedSourceTable }}
      </span>

      <!-- Display 'Themes' -->
      <span
        v-for="(theme, index) in formattedTheme"
        :key="index"
        class="label-theme"
      >
        {{ theme }}
      </span>
    </div>

    <!-- Right side of the header with "Open" link, only shown if showOpenLink is true -->
    <div v-if="showOpenLink">
      <NuxtLink :to="getLink()" style="display: inline-block">Open</NuxtLink>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps } from 'vue'

// Props
const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
  cardType: {
    type: String,
    required: true,
  },
  showOpenLink: {
    type: Boolean,
    default: true,
  },
})

// Computed property for "jurisdiction" to handle multiple field options and duplicates
const formattedJurisdiction = computed(() => {
  const jurisdictionString =
    props.resultData['Jurisdiction name'] ||
    props.resultData['Jurisdiction Names'] ||
    props.resultData['Name (from Jurisdiction)'] ||
    ''

  if (!jurisdictionString) {
    return [] // Return an empty array if no jurisdiction is found
  }

  // Split by comma, trim each item, and remove duplicates
  return [...new Set(jurisdictionString.split(',').map((item) => item.trim()))]
})

// Display `cardType` if available, or use `resultData.source_table`
// this works!
const formattedSourceTable = computed(() => {
  return props.cardType || props.resultData?.source_table || ''
})

const adjustedSourceTable = computed(() => {
  // Use the result from `formattedSourceTable` and apply label adjustments
  switch (formattedSourceTable.value) {
    case 'Court decisions':
      return 'Court decision'
    case 'Answers':
      return 'Question'
    case 'Legislation':
      return 'Legal Instrument'
    // Add more adjustments as needed
    default:
      return formattedSourceTable.value || '' // Fallback if no match
  }
})

const labelColorClass = computed(() => {
  switch (formattedSourceTable.value) {
    case 'Court decisions':
      return 'label-court-decision'
    case 'Answers':
    case 'Question':
      return 'label-question'
    case 'Legislation':
      return 'label-legal-instrument'
    default:
      return '' // No color for unknown labels
  }
})

const formattedTheme = computed(() => {
  const themes = props.resultData.Themes

  if (!themes || themes === 'None') {
    return [] // Return an empty array to avoid rendering issues
  }
  // Split the string into an array, trim each item, and filter out duplicates using Set
  return [...new Set(themes.split(',').map((theme) => theme.trim()))]
})

// Methods
function getLink() {
  // Determine the correct link based on the card type and resultData
  switch (props.cardType) {
    case 'Answers':
      return `/question/${props.resultData.id}`
    case 'Court decisions':
      return `/court-decision/${props.resultData.id}`
    case 'Legislation':
      return `/legal-instrument/${props.resultData.id}`
    default:
      return '#'
  }
}
</script>

<style scoped>
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
