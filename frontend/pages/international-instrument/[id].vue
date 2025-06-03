<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="processedInternationalInstrument"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
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
          <InfoTooltip
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import BaseLegalContent from '~/components/legal/BaseLegalContent.vue'
import InfoTooltip from '~/components/ui/InfoTooltip.vue'
import { useApiFetch } from '~/composables/useApiFetch'
import { useDetailDisplay } from '~/composables/useDetailDisplay'
import { internationalInstrumentConfig } from '~/config/pageConfigs'
import RelatedLiterature from '~/components/literature/RelatedLiterature.vue'
import LoadingBar from '~/components/layout/LoadingBar.vue'
import { useHead } from '#imports'

const config = useRuntimeConfig()
const route = useRoute()
const router = useRouter()

const {
  loading,
  error,
  data: internationalInstrument,
  fetchData,
} = useApiFetch()
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

// Fetch all provisions from International Legal Provisions table
const provisions = ref([])
const provisionsLoading = ref(false)
const provisionsError = ref(null)

async function fetchProvisions() {
  provisionsLoading.value = true
  provisionsError.value = null
  try {
    const response = await fetch(
      `${config.public.apiBaseUrl}/search/full_table`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ table: 'International Legal Provisions' }),
      }
    )
    if (!response.ok) throw new Error('Failed to fetch provisions')
    let data = await response.json()
    // Sort by Interface Order (ascending, starts with 0)
    data = data.slice().sort((a, b) => {
      const aOrder =
        typeof a['Interface Order'] === 'number'
          ? a['Interface Order']
          : Number(a['Interface Order']) || 0
      const bOrder =
        typeof b['Interface Order'] === 'number'
          ? b['Interface Order']
          : Number(b['Interface Order']) || 0
      return aOrder - bOrder
    })
    provisions.value = data
  } catch (err) {
    provisionsError.value = err.message || 'Error fetching provisions'
    provisions.value = []
  } finally {
    provisionsLoading.value = false
  }
}

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
    useHead({ title: pageTitle })
  },
  { immediate: true }
)

onMounted(async () => {
  try {
    await fetchData({
      table: 'International Instruments',
      id: route.params.id,
    })
    await fetchProvisions()
  } catch (err) {
    if (err.isNotFound) {
      router.push({
        path: '/error',
        query: { message: `International instrument not found` },
      })
    } else {
      console.error('Error fetching international instrument:', err)
    }
  }
})
</script>
