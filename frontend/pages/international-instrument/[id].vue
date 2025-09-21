<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="processedInternationalInstrument"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    :showSuggestEdit="true"
    sourceTable="International Instrument"
  >
    <template #literature>
      <section class="section-gap p-0 m-0">
        <RelatedLiterature
          :literature-id="processedInternationalInstrument?.Literature"
          :valueClassMap="valueClassMap['Literature']"
          :showLabel="true"
          :emptyValueBehavior="
            internationalInstrumentConfig.keyLabelPairs.find(
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

    <template #selected-provisions>
      <section class="section-gap p-0 m-0">
        <p class="label mt-12 mb-[-24px]">
          {{
            computedKeyLabelPairs.find(
              (pair) => pair.key === 'Selected Provisions'
            )?.label || 'Selected Provisions'
          }}
          <InfoPopover
            v-if="
              computedKeyLabelPairs.find(
                (pair) => pair.key === 'Selected Provisions'
              )?.tooltip
            "
            :text="
              computedKeyLabelPairs.find(
                (pair) => pair.key === 'Selected Provisions'
              )?.tooltip
            "
          />
        </p>
        <div :class="valueClassMap['Selected Provisions']">
          <div v-if="provisionsLoading">
            <LoadingBar class="!mt-8" />
          </div>
          <div v-else-if="provisionsError">{{ provisionsError }}</div>
          <div v-else-if="provisions.length">
            <BaseLegalContent
              v-for="(provision, index) in provisions"
              :key="index"
              :title="
                provision['Title of the Provision'] +
                (processedInternationalInstrument
                  ? ', ' +
                    (processedInternationalInstrument['Abbreviation'] ||
                      processedInternationalInstrument['Title (in English)'])
                  : '')
              "
              :anchorId="normalizeAnchorId(provision['Title of the Provision'])"
            >
              <template #default>
                {{ provision['Full Text'] }}
              </template>
            </BaseLegalContent>
          </div>
          <div v-else>No provisions found.</div>
        </div>
      </section>
    </template>
  </BaseDetailLayout>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import BaseLegalContent from '@/components/legal/BaseLegalContent.vue'
import InfoPopover from '~/components/ui/InfoPopover.vue'
import { useRecordDetails } from '@/composables/useRecordDetails'
import { useDetailDisplay } from '@/composables/useDetailDisplay'
import { internationalInstrumentConfig } from '@/config/pageConfigs'
import RelatedLiterature from '@/components/literature/RelatedLiterature.vue'
import LoadingBar from '@/components/layout/LoadingBar.vue'
import { useInternationalLegalProvisions } from '@/composables/useInternationalLegalProvisions'
import { useHead } from '#imports'

const config = useRuntimeConfig()
const route = useRoute()
const router = useRouter()

// Use TanStack Vue Query for data fetching
const table = ref('International Instruments')
const id = ref(route.params.id)

const {
  data: internationalInstrument,
  isLoading: loading,
  error,
} = useRecordDetails(table, id)
const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  internationalInstrument,
  internationalInstrumentConfig
)

const processedInternationalInstrument = computed(() => {
  if (!internationalInstrument.value) return null
  return {
    ...internationalInstrument.value,
    'Title (in English)':
      internationalInstrument.value['Title (in English)'] ||
      internationalInstrument.value['Name'],
    Date: internationalInstrument.value['Date'],
    URL:
      internationalInstrument.value['URL'] ||
      internationalInstrument.value['Link'],
  }
})

// Provisions via composable
const {
  data: provisions,
  isLoading: provisionsLoading,
  error: provisionsError,
} = useInternationalLegalProvisions()

function normalizeAnchorId(str) {
  if (!str) return ''
  // Remove accents/circumflexes, replace whitespace with dash, lowercase
  return str
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .replace(/\s+/g, '-')
    .replace(/[^a-zA-Z0-9\-_]/g, '')
    .toLowerCase()
}

// Set dynamic page title based on 'Name'
watch(
  internationalInstrument,
  (newVal) => {
    if (!newVal) return
    const name = newVal['Name']
    const pageTitle =
      name && name.trim() ? `${name} — CoLD` : 'International Instrument — CoLD'
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
        query: { message: 'International instrument not found' },
      })
    } else if (newError) {
      console.error('Error fetching international instrument:', newError)
    }
  },
  { immediate: true }
)
</script>
