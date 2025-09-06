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
import { computed, onMounted } from 'vue'
import { useJurisdictionComparison } from '@/composables/useJurisdictionComparison'

// Accept processedAnswerData as a prop from parent
defineProps({
  formattedJurisdiction: {
    type: Object,
    required: true,
  },
})

const route = useRoute()
const { jurisdictionOptions, loadJurisdictions } = useJurisdictionComparison()

// Get the ISO3 code from the route params
const iso3Code = computed(() => {
  return route.params.id?.toUpperCase()
})

// Computed property to get 2 random ISO3 codes (excluding current jurisdiction)
const randomJurisdictionCodes = computed(() => {
  const availableOptions = jurisdictionOptions.value.filter(
    (option) =>
      option.alpha3Code &&
      option.alpha3Code.toUpperCase() !== iso3Code.value &&
      option.label !== 'Loading…'
  )

  if (availableOptions.length < 2) {
    return ['che', 'bra'] // fallback to original codes
  }

  // Shuffle array and take first 2
  const shuffled = [...availableOptions].sort(() => Math.random() - 0.5)
  return shuffled.slice(0, 2).map((option) => option.alpha3Code.toLowerCase())
})

// Computed property for the complete comparison URL
const comparisonUrl = computed(() => {
  if (!iso3Code.value) return '#'

  const codes = [iso3Code.value.toLowerCase(), ...randomJurisdictionCodes.value]

  return `/jurisdiction-comparison/${codes.join('+')}`
})

// Load jurisdictions when component mounts
onMounted(() => {
  if (
    jurisdictionOptions.value.length === 1 &&
    jurisdictionOptions.value[0].label === 'Loading…'
  ) {
    loadJurisdictions()
  }
})
</script>

<style scoped>
h3 {
  color: var(--color-cold-purple) !important;
}
</style>
