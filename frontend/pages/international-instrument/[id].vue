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

    <template #url="{ value }">
      <div v-if="value">
        <p class="label-key mb-2">Link</p>
        <a :href="value" target="_blank" rel="noopener noreferrer">
          {{ value }}
        </a>
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
      <section class="mt-8">
        <span class="label">Selected Provisions</span>
        <p class="text-gray-300 mt-2">Coming soon</p>
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

onMounted(async () => {
  try {
    await fetchData({
      table: 'International Instruments',
      id: route.params.id,
    })
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
