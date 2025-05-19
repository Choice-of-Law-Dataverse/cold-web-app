<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="processedInternationalInstrument"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="International Instrument"
  >
    <template #date="{ value }">
      <div v-if="value">
        <p class="label-key mb-2">Date</p>
        <p :class="valueClassMap['Date']">
          {{ formatDate(value) }}
        </p>
      </div>
    </template>

    <template #literature>
      <section>
        <RelatedLiterature
          :literature-id="processedInternationalInstrument?.Literature"
          :valueClassMap="valueClassMap['Literature']"
          :showLabel="true"
          :emptyValueBehavior="
            internationalInstrumentConfig.keyLabelPairs.find(
              (pair) => pair.key === 'Literature'
            )?.emptyValueBehavior
          "
          mode="id"
        />
      </section>
    </template>

    <template #selected-provisions>
      <section>
        <span class="label">Selected Provisions</span>
        <div :class="valueClassMap['Selected Provisions']">
          <div v-if="provisionsLoading">Loading provisions...</div>
          <div v-else-if="provisionsError">{{ provisionsError }}</div>
          <div v-else-if="provisions.length">
            <LegalProvision
              v-for="(provision, index) in provisions"
              :key="provision.id || provision.provisionId || index"
              :provisionId="provision.id || provision.provisionId"
              :class="index === 0 ? '-mt-8' : ''"
              :textType="'Full Text'"
              :instrumentTitle="
                processedInternationalInstrument
                  ? processedInternationalInstrument['Abbreviation'] ||
                    processedInternationalInstrument['Title (in English)']
                  : ''
              "
              @update:hasEnglishTranslation="hasEnglishTranslation = $event"
            />
          </div>
          <div v-else>No provisions found.</div>
        </div>
      </section>
    </template>
  </BaseDetailLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import { useApiFetch } from '~/composables/useApiFetch'
import { useDetailDisplay } from '~/composables/useDetailDisplay'
import { internationalInstrumentConfig } from '~/config/pageConfigs'
import RelatedLiterature from '~/components/literature/RelatedLiterature.vue'
import LegalProvision from '~/components/legal/LegalProvision.vue'

function logProvisionId(id) {
  console.log('provisionId:', id)
  return id
}

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
  console.log('API data:', internationalInstrument.value)
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

// New: Fetch all provisions for this instrument
const provisions = ref([])
const provisionsLoading = ref(false)
const provisionsError = ref(null)

async function fetchProvisions() {
  provisionsLoading.value = true
  provisionsError.value = null
  try {
    // Adjust this API call as needed for your backend
    // Example: /api/international-legal-provisions?instrumentId=...
    const instrumentId = route.params.id
    const response = await fetch(
      `/api/international-legal-provisions?instrumentId=${instrumentId}`
    )
    if (!response.ok) throw new Error('Failed to fetch provisions')
    const data = await response.json()
    provisions.value = data
  } catch (err) {
    provisionsError.value = err.message || 'Error fetching provisions'
    provisions.value = []
  } finally {
    provisionsLoading.value = false
  }
}

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
