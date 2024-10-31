<template>
  <div class="col-span-12">
    <UCard class="cold-ucard">
      <template #header>
        <UCardHeader :resultData="resultData" :cardType="cardType" />
      </template>

      <!-- Card content -->
      <div>
        <slot />
      </div>
    </UCard>
  </div>
</template>

<script setup>
import UCardHeader from './UCardHeader.vue'

// Define props
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
</script>

<style scoped></style>
