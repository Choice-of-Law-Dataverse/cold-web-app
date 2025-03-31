<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="processedLegalInstrument"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Legal Instrument"
  >
    <!-- Slot for Legal provisions -->
    <template #domestic-legal-provisions="{ value }">
      <div>
        <div v-if="value && value.trim()">
          <div class="label-key pb-4 pt-4">Selected Provisions</div>
          <LegalProvision
            v-for="(provisionId, index) in value.split(',')"
            :key="index"
            :provisionId="provisionId.trim()"
            :class="index === 0 ? 'no-margin' : ''"
            :textType="textType"
            @update:hasEnglishTranslation="hasEnglishTranslation = $event"
          />
        </div>
        <div v-else>
          <span>N/A</span>
        </div>
      </div>
    </template>
    <template #entry-into-force="{ value }">
      <p class="result-value-small">
        {{ formatDate(value) || 'N/A' }}
      </p>
    </template>

    <template #publication-date="{ value }">
      <p class="result-value-small">
        {{ formatDate(value) || 'N/A' }}
      </p>
    </template>
  </BaseDetailLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import LegalProvision from '~/components/legal/LegalProvision.vue'
import { useApiFetch } from '~/composables/useApiFetch'
import { useDetailDisplay } from '~/composables/useDetailDisplay'

const route = useRoute()
const textType = ref('Full Text of the Provision (English Translation)')
const hasEnglishTranslation = ref(false)

const { loading, error, data: legalInstrument, fetchData } = useApiFetch()

// Define the keys and labels for dynamic rendering
const keyLabelPairs = [
  { key: 'Title (in English)', label: 'Name' },
  { key: 'Official Title', label: 'Official Title' },
  { key: 'Date', label: 'Date' },
  { key: 'Entry Into Force', label: 'Entry Into Force' },
  { key: 'Publication Date', label: 'Publication Date' },
  { key: 'Domestic Legal Provisions', label: '' },
]

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(legalInstrument, keyLabelPairs)

// Debug the legal instrument data
watch(legalInstrument, (newValue) => {
  console.log('Legal Instrument Data:', newValue)
  if (newValue) {
    console.log('Domestic Legal Provisions:', newValue['Domestic Legal Provisions'])
  }
})

const processedLegalInstrument = computed(() => {
  if (!legalInstrument.value) return null
  return {
    ...legalInstrument.value,
    'Title (in English)': legalInstrument.value['Title (in English)'] || legalInstrument.value['Official Title']
  }
})

onMounted(() => {
  fetchData({
    table: 'Domestic Instruments',
    id: route.params.id,
  })
})
</script>
