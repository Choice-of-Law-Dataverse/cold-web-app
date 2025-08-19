<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <UCard class="cold-ucard">
          <div class="popular-searches-container flex flex-col gap-8">
            <!-- Title Section -->
            <div>
              <h3 class="text-left md:whitespace-nowrap mb-1">
                <NuxtLink
                  v-if="jurisdictionCode"
                  :to="`/jurisdiction/${jurisdictionCode.toLowerCase()}`"
                >
                  Country report for
                  {{
                    processedAnswerData?.Jurisdictions || 'this jurisdiction'
                  }}
                </NuxtLink>
                <span v-else>
                  Country report for
                  {{
                    processedAnswerData?.Jurisdictions || 'this jurisdiction'
                  }}
                </span>
              </h3>
              <span class="result-value-small">
                The country report provides detailed information, answers, and
                more on
                {{ processedAnswerData?.Jurisdictions || 'this jurisdiction' }}
              </span>
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed } from 'vue'

// Accept processedAnswerData as a prop from parent
const props = defineProps({
  processedAnswerData: {
    type: Object,
    required: true,
  },
})

// Computed property to handle different property name variations
const jurisdictionCode = computed(() => {
  return (
    props.processedAnswerData?.['Jurisdictions Alpha-3 code'] ||
    props.processedAnswerData?.['Jurisdictions Alpha-3 Code']
  )
})
</script>

<style scoped>
h3 {
  color: var(--color-cold-purple) !important;
}

/* :deep(span.result-value-small) {
  margin-top: 24px !important;
} */
</style>
