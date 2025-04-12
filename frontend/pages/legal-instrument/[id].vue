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
      <section>
        <span class="label">Selected Provisions</span>
        <div :class="valueClassMap['Domestic Legal Provisions']">
          <div v-if="value && value.trim()">
            <LegalProvision
              v-for="(provisionId, index) in value.split(',')"
              :key="index"
              :provisionId="provisionId.trim()"
              :class="index === 0 ? 'no-margin' : ''"
              :textType="textType"
              :instrumentTitle="
                processedLegalInstrument
                  ? processedLegalInstrument['Abbreviation'] ||
                    processedLegalInstrument['Title (in English)']
                  : ''
              "
              @update:hasEnglishTranslation="hasEnglishTranslation = $event"
            />
          </div>
          <div v-else>
            <span>N/A</span>
          </div>
        </div>
      </section>
    </template>
    <template #entry-into-force="{ value }">
      <div v-if="value">
        <p class="label-key">Entry Into Force</p>
        <p :class="valueClassMap['Entry Into Force']">
          {{ formatDate(value) }}
        </p>
      </div>
    </template>

    <template #publication-date="{ value }">
      <div v-if="value">
        <p class="label-key">Publication Date</p>
        <p :class="valueClassMap['Publication Date']">
          {{ formatDate(value) }}
        </p>
      </div>
    </template>
  </BaseDetailLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import LegalProvision from '~/components/legal/LegalProvision.vue'
import { useApiFetch } from '~/composables/useApiFetch'
import { useDetailDisplay } from '~/composables/useDetailDisplay'
import { legalInstrumentConfig } from '~/config/pageConfigs'

const route = useRoute()
const router = useRouter()
const textType = ref('Full Text of the Provision (English Translation)')
const hasEnglishTranslation = ref(false)

const { loading, error, data: legalInstrument, fetchData } = useApiFetch()

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  legalInstrument,
  legalInstrumentConfig
)

const processedLegalInstrument = computed(() => {
  if (!legalInstrument.value) {
    return null
  }
  return {
    ...legalInstrument.value,
    'Title (in English)':
      legalInstrument.value['Title (in English)'] ||
      legalInstrument.value['Official Title'],
  }
})

onMounted(async () => {
  try {
    await fetchData({
      table: 'Domestic Instruments',
      id: route.params.id,
    })
  } catch (err) {
    if (err.isNotFound) {
      router.push({
        path: '/error',
        query: { message: `${err.table} not found` },
      })
    } else {
      console.error('Error fetching legal instrument:', err)
    }
  }
})
</script>
