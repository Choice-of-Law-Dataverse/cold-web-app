<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="processedRegionalInstrument"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Regional Instrument"
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

    <!-- <template #related-literature-temp>
      <section class="mt-8">
        <span class="label">Related Literature</span>
        <p class="text-gray-300 mt-2">Coming soon</p>
      </section>
    </template> -->
    <template #literature>
      <section>
        <RelatedLiterature
          :literature-id="processedRegionalInstrument?.Literature"
          :literature-title="literatureTitle"
          :valueClassMap="valueClassMap['Related Literature']"
          :showLabel="false"
          :emptyValueBehavior="
            keyLabelPairs.find((pair) => pair.key === 'Literature')
              ?.emptyValueBehavior
          "
          use-id
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
import { regionalInstrumentConfig } from '~/config/pageConfigs'
import RelatedLiterature from '~/components/literature/RelatedLiterature.vue'

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
