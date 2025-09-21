<template>
  <main class="px-6">
    <div class="mx-auto w-full max-w-container">
      <div class="col-span-12">
        <UCard class="cold-ucard">
          <div class="popular-searches-container flex flex-col gap-8">
            <!-- Title Section -->
            <div>
              <h3 class="text-left md:whitespace-nowrap">
                <NuxtLink
                  v-if="formattedJurisdiction?.Name && iso3Code"
                  :to="comparisonUrl"
                >
                  Compare
                  {{ formattedJurisdiction?.Name || 'this jurisdiction' }} with
                  other jurisdictions
                </NuxtLink>
                <span v-else>
                  Compare
                  {{ formattedJurisdiction?.Name || 'this jurisdiction' }} with
                  other jurisdictions
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
import { useRoute } from 'vue-router'
import { computed } from 'vue'

// Accept processedAnswerData as a prop from parent
defineProps({
  formattedJurisdiction: {
    type: Object,
    required: true,
  },
})

const route = useRoute()

// Get the ISO3 code from the route params
const iso3Code = computed(() => {
  return route.params.id?.toUpperCase()
})

// Computed property to choose a fixed second jurisdiction code
// Use 'ago' by default; if current is 'ago', use 'arg'
const secondJurisdictionCode = computed(() => {
  const current = iso3Code.value?.toLowerCase()
  return current === 'ago' ? 'arg' : 'ago'
})

// Computed property for the complete comparison URL
const comparisonUrl = computed(() => {
  if (!iso3Code.value) return '#'

  const codes = [iso3Code.value.toLowerCase(), secondJurisdictionCode.value]

  return `/jurisdiction-comparison/${codes.join('+')}`
})
</script>

<style scoped>
h3 {
  color: var(--color-cold-purple) !important;
}
</style>
