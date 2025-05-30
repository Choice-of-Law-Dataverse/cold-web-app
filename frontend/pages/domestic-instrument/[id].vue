<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="processedLegalInstrument"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Domestic Instrument"
  >
    <!-- Slot for Legal provisions -->
    <template #domestic-legal-provisions="{ value }">
      <!-- Only render if value exists and is not "N/A" -->
      <section
        v-if="value && value.trim() && value.trim() !== 'N/A'"
        class="section-gap p-0 m-0"
      >
        <p class="label mt-12 mb-[-24px]">
          {{
            computedKeyLabelPairs.find(
              (pair) => pair.key === 'Domestic Legal Provisions'
            )?.label || 'Selected Provisions'
          }}
          <InfoTooltip
            v-if="
              computedKeyLabelPairs.find(
                (pair) => pair.key === 'Domestic Legal Provisions'
              )?.tooltip
            "
            :text="
              computedKeyLabelPairs.find(
                (pair) => pair.key === 'Domestic Legal Provisions'
              )?.tooltip
            "
          />
        </p>
        <div :class="valueClassMap['Domestic Legal Provisions']">
          <div v-if="value && value.trim()">
            <LegalProvision
              v-for="(provisionId, index) in value.split(',')"
              :key="index"
              :provisionId="provisionId"
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
        </div>
      </section>
    </template>
  </BaseDetailLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import LegalProvision from '~/components/legal/LegalProvision.vue'
import InfoTooltip from '~/components/ui/InfoTooltip.vue'
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
        query: { message: `Domestic instrument not found` },
      })
    } else {
      console.error('Error fetching legal instrument:', err)
    }
  }
})
</script>
