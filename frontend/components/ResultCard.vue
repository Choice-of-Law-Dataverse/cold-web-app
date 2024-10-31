<template>
  <div class="col-span-12">
    <UCard class="cold-ucard">
      <template #header>
        <div class="header-container">
          <!-- Left side of the header -->
          <div class="header-left label">
            <!-- Display 'Name (from Jurisdiction)' or alternatives -->
            <span v-if="jurisdiction" class="label-jurisdiction">{{
              jurisdiction
            }}</span>

            <!-- Display 'source_table' -->
            <span
              v-if="formattedSourceTable"
              :class="['label', labelColorClass]"
            >
              {{ formattedSourceTable }}
            </span>

            <!-- Display 'Themes' -->
            <span v-if="formattedTheme" class="label-theme">
              {{ formattedTheme }}
            </span>
          </div>

          <!-- Right side of the header with "Open" link -->
          <div class="header-right">
            <NuxtLink v-if="resultData.id" :to="getLink()">Open</NuxtLink>
          </div>
        </div>
      </template>

      <!-- Card content -->
      <div>
        <slot />
      </div>
    </UCard>
  </div>
</template>

<script setup>
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

// Computed property for "jurisdiction" to handle multiple field options
const jurisdiction = computed(() => {
  return (
    props.resultData['Jurisdiction name'] ||
    props.resultData['Jurisdiction Names'] ||
    props.resultData['Name (from Jurisdiction)'] ||
    null
  )
})

// Computed property for "formattedSourceTable" to overwrite specific themes
const formattedSourceTable = computed(() => {
  const source_table = props.resultData.source_table
  if (source_table === 'Court decisions') {
    return 'Court decision'
  }
  if (source_table === 'Answers') {
    return 'Question'
  }
  if (source_table === 'Legislation') {
    return 'Legal Instrument'
  }
  // Add more overwrites as needed
  return source_table
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

// Computed property for "formattedTheme" to overwrite specific themes
const formattedTheme = computed(() => {
  const Themes = props.resultData.Themes
  if (Themes === 'None') {
    return null
  }
  return Themes
})

// Methods
const getLink = () => {
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

.header-right {
  /* Aligns the "Open" link to the right */
}
</style>
