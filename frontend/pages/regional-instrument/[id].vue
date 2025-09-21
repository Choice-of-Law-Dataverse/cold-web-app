<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="processedRegionalInstrument"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    :showSuggestEdit="true"
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
        <p class="label mt-12 mb-[-24px] flex flex-row items-center">
          {{
            computedKeyLabelPairs.find(
              (pair) => pair.key === 'Regional Legal Provisions'
            )?.label || 'Selected Provisions'
          }}
          <InfoPopover
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
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import { useRecordDetails } from '@/composables/useRecordDetails'
import { useDetailDisplay } from '@/composables/useDetailDisplay'
import { regionalInstrumentConfig } from '@/config/pageConfigs'
import RelatedLiterature from '@/components/literature/RelatedLiterature.vue'
import LegalProvision from '@/components/legal/LegalProvision.vue'
import InfoPopover from '~/components/ui/InfoPopover.vue'
import { useHead } from '#imports'

const route = useRoute()
const router = useRouter()

// Use TanStack Vue Query for data fetching
const table = ref('Regional Instruments')
const id = ref(route.params.id)

const {
  data: regionalInstrument,
  isLoading: loading,
  error,
} = useRecordDetails(table, id)
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

// Set dynamic page title based on 'Abbreviation'
watch(
  processedRegionalInstrument,
  (newVal) => {
    if (!newVal) return
    const abbr = newVal['Abbreviation']
    const pageTitle =
      abbr && abbr.trim() ? `${abbr} — CoLD` : 'Regional Instrument — CoLD'
    useHead({
      title: pageTitle,
      link: [
        {
          rel: 'canonical',
          href: `https://cold.global${route.fullPath}`,
        },
      ],
      meta: [
        {
          name: 'description',
          content: pageTitle,
        },
      ],
    })
  },
  { immediate: true }
)

// Handle not found errors
watch(
  error,
  (newError) => {
    if (newError?.isNotFound) {
      router.push({
        path: '/error',
        query: { message: 'Regional instrument not found' },
      })
    } else if (newError) {
      console.error('Error fetching regional instrument:', newError)
    }
  },
  { immediate: true }
)
</script>
