<template>
  <UCard>
    <div style="position: relative">
      <!-- "Open" link in the top-right corner -->
      <NuxtLink
        v-if="resultData.id"
        :to="getLink()"
        style="position: absolute; top: 10px; right: 10px"
      >
        Open
      </NuxtLink>

      <!-- Content slot for specific result type details -->
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
