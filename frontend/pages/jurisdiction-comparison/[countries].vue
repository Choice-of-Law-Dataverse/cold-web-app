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
            <h1 class="mb-16">Jurisdiction Comparison</h1>
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
              <JCQuestions title="No Theme" :questionIDs="['01.3-']" />
              <JCQuestions
                title="Party Autonomy, Freedom of Choice"
                :questionIDs="[
                  '03-PA',
                  '04-PA',
                  '06-PA',
                  '06.1-PA',
                  '06.2-PA',
                  '07-PA',
                  '08-PA',
                  '08.1-PA',
                ]"
              />
              <JCQuestions
                title="Party Autonomy, Freedom of Choice, Dépeçage"
                :questionIDs="['05-PA']"
              />
              <JCQuestions
                title="Party Autonomy, Freedom of Choice, Partial Choice"
                :questionIDs="['05.1-PA']"
              />
              <JCQuestions
                title="Party Autonomy, Rules of Law"
                :questionIDs="['09-FoC', '10-FoC', '11-FoC', '11.1-FoC']"
              />
              <JCQuestions
                title="Party Autonomy, Tacit Choice"
                :questionIDs="[
                  '12-TC',
                  '13-TC',
                  '14-TC',
                  '15-TC',
                  '16.1-TC',
                  '16.2-TC',
                  '16.3-TC',
                  '16.4-TC',
                  '16.5-TC',
                  '17-TC',
                  '17.1-TC',
                  '18-TC',
                  '19-TC',
                  '19.1-TC',
                ]"
              />
              <JCQuestions
                title="Overriding Mandatory Rules"
                :questionIDs="['20-MR', '21-MR', '21.1-MR', '22-MR', '22.1-MR']"
              />
              <JCQuestions
                title="Public Policy"
                :questionIDs="['23-PP', '23.1-PP', '24-PP']"
              />
              <JCQuestions
                title="Public Policy, Absence of Choice"
                :questionIDs="['25-PP']"
              />
              <JCQuestions
                title="Arbitration, Codification, HCCH Principles"
                :questionIDs="['26-Arb']"
              />
              <JCQuestions
                title="Arbitration, Overriding Mandatory Rules, Public Policy"
                :questionIDs="['27-Arb']"
              />
              <JCQuestions
                title="Arbitration"
                :questionIDs="['28-Arb', '28.1-Arb']"
              />
              <JCQuestions
                title="Absence of Choice"
                :questionIDs="[
                  '29-AoC',
                  '30-AoC',
                  '30.1-AoC',
                  '30.2-AoC',
                  '31-AoC',
                  '32-AoC',
                  '33-FV',
                ]"
              />
              <JCQuestions
                title="Employment Contracts, Consumer Contracts"
                :questionIDs="['34-FV']"
              />
              <JCQuestions
                title="HCCH Principles"
                :questionIDs="['35-FV', '36-FV']"
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
import { useHead } from '#app'

const route = useRoute()

// Set static page title
useHead({
  title: 'Compare Jurisdictions — CoLD',
  link: [
    {
      rel: 'canonical',
      href: `https://cold.global${route.fullPath}`,
    },
  ],
  meta: [
    {
      name: 'description',
      content: 'Compare Jurisdictions — CoLD',
    },
  ],
})

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
