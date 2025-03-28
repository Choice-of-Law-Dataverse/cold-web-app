<template>
  <div class="col-span-12">
    <UCard class="cold-ucard">
      <template #header>
        <UCardHeader
          :resultData="resultData"
          :cardType="cardType"
          :showSuggestEdit="false"
        />
      </template>

      <!-- Card content -->
      <div>
        <slot />
      </div>
    </UCard>
  </div>
</template>

<script setup>
import UCardHeader from '../ui/BaseCardHeader.vue'

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

<style scoped>
.cold-ucard {
  margin-bottom: 24px;
}

.cold-ucard ::v-deep(.px-4) {
  padding-left: 32px !important;
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
</style>
