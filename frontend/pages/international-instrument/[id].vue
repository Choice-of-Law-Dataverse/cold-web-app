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
            <BaseLegalContent
              v-for="(provision, index) in provisions"
              :key="index"
              :title="provision['Title of the Provision']"
              :anchorId="`provision-${index}`"
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import BaseLegalContent from '~/components/legal/BaseLegalContent.vue'
import { useApiFetch } from '~/composables/useApiFetch'
import { useDetailDisplay } from '~/composables/useDetailDisplay'
import { internationalInstrumentConfig } from '~/config/pageConfigs'
import RelatedLiterature from '~/components/literature/RelatedLiterature.vue'

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
