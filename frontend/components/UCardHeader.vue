<template>
  <div class="header-container">
    <!-- Left side of the header -->
    <div class="header-left label">
      <!-- Display 'Name (from Jurisdiction)' or alternatives -->
      <span
        v-for="(jurisdictionString, index) in formattedJurisdiction"
        :key="index"
        class="label-jurisdiction"
      >
        {{ jurisdictionString }}
      </span>

      <!-- Display 'source_table' -->
      <span v-if="formattedSourceTable" :class="['label', labelColorClass]">
        {{ formattedSourceTable }}
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

    <!-- Right side of the header with "Open" link -->
    <div>
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
})

// Log to debug
// console.log('UCardHeader - cardType:', props.cardType) // Should print "Court Decision"
// console.log('UCardHeader - resultData:', props.resultData)

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

// Computed property for "formattedSourceTable" to overwrite specific themes
// const formattedSourceTable = computed(() => {
//   const source_table = props.resultData?.source_table
//   if (source_table === 'Court decisions') {
//     return 'Court decision'
//   }
//   if (source_table === 'Answers') {
//     return 'Question'
//   }
//   if (source_table === 'Legislation') {
//     return 'Legal Instrument'
//   }
//   // Add more overwrites as needed
//   return source_table || ''
// })

// Display `cardType` if available, or use `resultData.source_table`
const formattedSourceTable = computed(() => {
  return props.cardType || props.resultData?.source_table || ''
})

const labelColorClass = computed(() => {
  switch (formattedSourceTable.value) {
    case 'Court decision':
      return 'label-court-decision'
    case 'Question':
      return 'label-question'
    case 'Legal Instrument':
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

.header-left span {
  margin-right: 8px;
}
</style>
