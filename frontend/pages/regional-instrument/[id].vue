<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="processedRegionalInstrument"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Regional Instrument"
  >
    <template #literature>
      <section class="section-gap p-0 m-0">
        <RelatedLiterature
          :literature-id="processedRegionalInstrument?.Literature"
          :valueClassMap="valueClassMap['Literature']"
          :showLabel="true"
          :emptyValueBehavior="
            regionalInstrumentConfig.keyLabelPairs.find(
              (pair) => pair.key === 'Literature'
            )?.emptyValueBehavior
          "
          :tooltip="
            computedKeyLabelPairs.find((pair) => pair.key === 'Literature')
              ?.tooltip
          "
          mode="id"
        />
      </section>
    </template>

    <!-- Slot for Legal provisions -->
    <template #regional-legal-provisions="{ value }">
      <!-- Only render if value exists and is not "N/A" -->
      <section
        v-if="value && value.trim() && value.trim() !== 'N/A'"
        class="section-gap p-0 m-0"
      >
        <p class="label mt-12 mb-[-24px]">
          {{
            computedKeyLabelPairs.find(
              (pair) => pair.key === 'Regional Legal Provisions'
            )?.label || 'Selected Provisions'
          }}
          <InfoTooltip
            v-if="
              computedKeyLabelPairs.find(
                (pair) => pair.key === 'Regional Legal Provisions'
              )?.tooltip
            "
            :text="
              computedKeyLabelPairs.find(
                (pair) => pair.key === 'Regional Legal Provisions'
              )?.tooltip
            "
          />
        </p>
        <div :class="valueClassMap['Regional Legal Provisions']">
          <div v-if="value && value.trim()">
            <LegalProvision
              v-for="(provisionId, index) in value.split(',')"
              :key="index"
              :provisionId="provisionId"
              :textType="textType"
              :instrumentTitle="
                processedRegionalInstrument
                  ? processedRegionalInstrument['Abbreviation'] ||
                    processedRegionalInstrument['Title']
                  : ''
              "
              table="Regional Legal Provisions"
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
import { useApiFetch } from '~/composables/useApiFetch'
import { useDetailDisplay } from '~/composables/useDetailDisplay'
import { regionalInstrumentConfig } from '~/config/pageConfigs'
import RelatedLiterature from '~/components/literature/RelatedLiterature.vue'
import LegalProvision from '~/components/legal/LegalProvision.vue'
import InfoTooltip from '~/components/ui/InfoTooltip.vue'

const route = useRoute()
const router = useRouter()
const { loading, error, data: regionalInstrument, fetchData } = useApiFetch()
const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  regionalInstrument,
  regionalInstrumentConfig
)

const processedRegionalInstrument = computed(() => {
  if (!regionalInstrument.value) return null
  return {
    ...regionalInstrument.value,
    'Title (in English)':
      regionalInstrument.value['Title (in English)'] ||
      regionalInstrument.value['Name'],
    Date: regionalInstrument.value['Date'],
    URL: regionalInstrument.value['URL'] || regionalInstrument.value['Link'],
  }
})

onMounted(async () => {
  try {
    await fetchData({
      table: 'Regional Instruments',
      id: route.params.id,
    })
  } catch (err) {
    if (err.isNotFound) {
      router.push({
        path: '/error',
        query: { message: `Regional instrument not found` },
      })
    } else {
      console.error('Error fetching regional instrument:', err)
    }
  }
})
</script>
