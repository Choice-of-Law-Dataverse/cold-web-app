<template>
  <UCard>
    <template #header>
      <div class="header-container">
        <!-- Left side of the header -->
        <div class="header-left">
          <!-- Display 'Name (from Jurisdiction)' or alternatives -->
          <span v-if="jurisdiction">{{ jurisdiction }}</span>

          <!-- Display 'source_table' -->
          <span v-if="resultData.source_table" class="source-table">
            {{ resultData.source_table }}
          </span>

          <!-- Display 'Themes' -->
          <span v-if="resultData.Themes" class="themes">
            {{ resultData.Themes }}
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
