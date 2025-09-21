<template>
  <div class="col-span-12">
    <UCard class="cold-ucard">
      <template #header>
        <template v-if="cardType === 'Loading'">
          <USkeleton
            class="h-5 mt-0.5 mb-0.5 w-[100px] rounded-none"
            style="background-color: var(--color-cold-gray-alpha)"
          />
        </template>
        <template v-else>
          <BaseCardHeader
            v-if="resultData"
            :resultData="resultData"
            :cardType="cardType"
            :showOpenLink="true"
            :formattedJurisdiction="formattedJurisdiction"
            :formattedTheme="formattedTheme"
            :showSuggestEdit="false"
          />
        </template>
      </template>

      <!-- Card content -->
      <div>
        <slot />
      </div>
    </UCard>
  </div>
</template>

<script setup>
import { UCard } from '#components'
import BaseCardHeader from '@/components/ui/BaseCardHeader.vue'

// Define props
const props = defineProps({
  resultData: {
    type: Object,
    required: false, // Changed: no longer required
    default: () => ({}),
  },
  cardType: {
    type: String,
    required: true,
  },
  formattedTheme: {
    type: Array,
    required: false,
    default: () => [],
  },
  formattedJurisdiction: {
    type: Array,
    required: false,
    default: () => [],
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
