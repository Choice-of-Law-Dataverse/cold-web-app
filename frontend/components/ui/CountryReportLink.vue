<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <UCard class="cold-ucard">
          <div class="popular-searches-container flex flex-col gap-8">
            <!-- Title Section -->
            <div>
              <h3 class="text-left md:whitespace-nowrap">
                <NuxtLink
                  v-if="jurisdictionCode"
                  :to="`/jurisdiction/${jurisdictionCode.toLowerCase()}`"
                >
                  Go to the country report for
                  {{
                    processedAnswerData?.Jurisdictions || 'this jurisdiction'
                  }}
                </NuxtLink>
                <span v-else>
                  Go to the country report for
                  {{
                    processedAnswerData?.Jurisdictions || 'this jurisdiction'
                  }}
                </span>
              </h3>
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
</style>
