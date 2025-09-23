<template>
  <div>
    <!-- Main content in BaseDetailLayout -->
    <BaseDetailLayout
      :loading="false"
      :result-data="{}"
      :key-label-pairs="[]"
      :value-class-map="{}"
      :show-header="false"
      source-table=""
    >
      <template #full-width>
        <!-- Create a container that ensures proper sticky behavior -->
        <div class="relative min-h-screen">
          <div class="px-6 py-4 md:pt-8">
            <!-- Sticky filters positioned within BaseDetailLayout -->
            <h1 class="mb-16">Jurisdiction Comparison</h1>
            <JCStickyFilters :initial-countries="validatedCountryCodes" />

            <!-- Content area with sufficient height for sticky behavior -->
            <div class="relative md:mt-0">
              <JCOverview
                :selected-jurisdiction-codes="validatedCountryCodes"
              />
              <JCQuestions
                :show-caret="false"
                title="Main Questions"
                :question-i-ds="['03-PA', '07-PA', '08-PA', '09-FoC']"
              />
              <JCQuestions
                title="Codification"
                :question-i-ds="[
                  '01.1-P',
                  '01.2.1-P',
                  '01.2.2-P',
                  '01.2.3.1-P',
                  '01.2.3.2-P',
                  '01.2.3.3-P',
                  '01.2-P',
                  '01.3-',
                  '01-P',
                  '02-P',
                ]"
              />

              <JCQuestions
                title="Party Autonomy"
                :question-i-ds="[
                  '03-PA',
                  '04-PA',
                  '05.1-PA',
                  '05-PA',
                  '06.1-PA',
                  '06.2-PA',
                  '06-PA',
                  '07-PA',
                  '08.1-PA',
                  '08-PA',
                  '09-FoC',
                  '10-FoC',
                  '11.1-FoC',
                  '11-FoC',
                  '12-TC',
                  '13-TC',
                  '14-TC',
                  '15-TC',
                  '16.1-TC',
                  '16.2-TC',
                  '16.3-TC',
                  '16.4-TC',
                  '16.5-TC',
                  '17.1-TC',
                  '17-TC',
                  '18-TC',
                  '19.1-TC',
                  '19-TC',
                ]"
              />

              <JCQuestions
                title="Overriding Mandatory Rules"
                :question-i-ds="[
                  '20-MR',
                  '21.1-MR',
                  '21-MR',
                  '22.1-MR',
                  '22-MR',
                ]"
              />

              <JCQuestions
                title="Public Policy"
                :question-i-ds="['23.1-PP', '23-PP', '24-PP', '25-PP']"
              />

              <JCQuestions
                title="Arbitration"
                :question-i-ds="['26-Arb', '27-Arb', '28.1-Arb', '28-Arb']"
              />

              <JCQuestions
                title="Absence of Choice"
                :question-i-ds="[
                  '29-AoC',
                  '30.1-AoC',
                  '30.2-AoC',
                  '30-AoC',
                  '31-AoC',
                  '32-AoC',
                  '33-FV',
                ]"
              />

              <JCQuestions
                title="Employment and Consumer Contracts"
                :question-i-ds="['34-FV']"
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
import { useRoute } from 'vue-router'

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

// Parse and validate country codes from the URL parameter
const validatedCountryCodes = computed(() => {
  const countries = route.params.countries
  if (typeof countries !== 'string') return []
  // Split by '+' and convert to uppercase for consistency
  const codes = countries.split('+').map((code) => code.toUpperCase())
  // Accept 2 or 3 country codes; otherwise, let defaults apply
  return codes.length === 2 || codes.length === 3 ? codes : []
})
</script>
