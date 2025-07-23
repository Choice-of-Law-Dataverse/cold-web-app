<template>
  <div>
    <!-- Main content in BaseDetailLayout -->
    <BaseDetailLayout
      :loading="false"
      :resultData="{}"
      :keyLabelPairs="[]"
      :valueClassMap="{}"
      sourceTable=""
    >
      <template #full-width>
        <!-- Create a container that ensures proper sticky behavior -->
        <div class="relative min-h-screen">
          <div class="px-6 py-4 md:pt-8">
            <!-- Sticky filters positioned within BaseDetailLayout -->
            <JCStickyFilters :initialCountries="validatedCountryCodes" />

            <!-- Content area with sufficient height for sticky behavior -->
            <div class="md:mt-0 relative">
              <JCOverview />
              <JCQuestions
                :showCaret="false"
                title="Main Questions"
                :questionIDs="['03-PA', '07-PA', '08-PA', '09-FoC']"
              />
              <JCQuestions
                title="Codification"
                :questionIDs="['01-P', '01.1-P', '01.2-P', '01.2.1-P']"
              />
              <JCQuestions
                title="Codification, HCCH Principles"
                :questionIDs="[
                  '01.2.2-P',
                  '01.2.3.1-P',
                  '01.2.3.2-P',
                  '01.2.3.3-P',
                  '02-P',
                ]"
              />
            </div>
          </div>
        </div>
      </template>
    </BaseDetailLayout>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import JCOverview from '@/pages/jurisdiction-comparison/JCOverview.vue'
import JCQuestions from '~/pages/jurisdiction-comparison/JCQuestions.vue'
import JCStickyFilters from '@/pages/jurisdiction-comparison/JCStickyFilters.vue'

const route = useRoute()

// Parse country codes from the URL parameter
const countryCodes = computed(() => {
  const countries = route.params.countries
  if (typeof countries === 'string') {
    // Split by '+' and convert to uppercase for consistency
    return countries.split('+').map((code) => code.toUpperCase())
  }
  return []
})

// Ensure we always have exactly 3 country codes
const validatedCountryCodes = computed(() => {
  const codes = countryCodes.value
  // If we don't have exactly 3 codes, return empty array to use defaults
  if (codes.length !== 3) {
    return []
  }
  return codes
})
</script>
