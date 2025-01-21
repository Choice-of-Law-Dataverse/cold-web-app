<template>
  <div class="header-container flex items-center justify-between">
    <!-- Left side of the header: Tags -->
    <div
      class="tags-container flex items-center gap-2 overflow-x-auto scrollbar-hidden"
    >
      <!-- Display 'Name (from Jurisdiction)' or alternatives -->
      <span
        v-for="(jurisdictionString, index) in formattedJurisdiction"
        :key="`jurisdiction-${index}`"
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
        :key="`theme-${index}`"
        class="label-theme"
      >
        {{ theme }}
      </span>
    </div>

    <!-- Right side of the header: "Open" link -->
    <div v-if="showOpenLink" class="flex-shrink-0 ml-4">
      <NuxtLink :to="getLink()" class="text-cold-blue hover:underline">
        Open
      </NuxtLink>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

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

/* Ensure horizontal scrolling for tags without a visible scrollbar */
.tags-container {
  overflow-x: auto;
  white-space: nowrap;
}

/* Hide the scrollbar for a cleaner look */
.scrollbar-hidden::-webkit-scrollbar {
  display: none; /* For Chrome, Safari, and Edge */
}
.scrollbar-hidden {
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}

/* Label styles for tags (jurisdiction, source_table, themes) */
.label-jurisdiction,
.label-theme,
.label {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  background-color: var(--color-cold-gray);
  border-radius: 0.25rem;
  white-space: nowrap;
}
</style>
