<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="processedRegionalInstrument"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Regional Instrument"
  />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import { useApiFetch } from '~/composables/useApiFetch'
import { useDetailDisplay } from '~/composables/useDetailDisplay'

// Minimal config for regional instruments
const regionalInstrumentConfig = {
  keyLabelPairs: [
    {
      key: 'Name',
      label: 'Name',
      emptyValueBehavior: { action: 'display', fallback: 'No name available' },
    },
    {
      key: 'Date',
      label: 'Date',
      emptyValueBehavior: { action: 'display', fallback: 'No date available' },
    },
    {
      key: 'URL',
      label: 'URL',
      emptyValueBehavior: { action: 'display', fallback: 'No URL available' },
    },
  ],
  valueClassMap: {
    Name: 'result-value-medium',
    Date: 'result-value-small',
    URL: 'result-value-small',
  },
}

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
    Name:
      regionalInstrument.value['Name'] ||
      regionalInstrument.value['Title (in English)'],
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
