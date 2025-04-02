<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="literature"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Literature"
  >
    <BaseCardHeader
      v-if="literature"
      :resultData="literature"
      :cardType="'Literature'"
      :showOpenLink="false"
      :showSuggestEdit="true"
    />
    <template #publication-title="{ value }">
      <div v-if="value && literature['Item Type'] !== 'book'">
        <p class="label-key -mb-1">Publication</p>
        <p class="result-value-small">
          {{ value }}
        </p>
      </div>
    </template>
    <template #publisher="{ value }">
      <div v-if="value && literature['Item Type'] === 'book'">
        <p class="label-key -mb-1">Publisher</p>
        <p class="result-value-small">
          {{ value }}
        </p>
      </div>
    </template>
    <template #url="{ value }">
      <div v-if="value">
        <p class="label-key -mb-1">Link</p>
        <p class="result-value-small">
          <a :href="value" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 hover:underline">
            {{ value }}
          </a>
        </p>
      </div>
    </template>
  </BaseDetailLayout>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import { useApiFetch } from '~/composables/useApiFetch'
import { useDetailDisplay } from '~/composables/useDetailDisplay'
import BaseCardHeader from '~/components/ui/BaseCardHeader.vue'
import { literatureConfig } from '~/config/pageConfigs'

const route = useRoute()
const router = useRouter()

const { loading, error, data: literature, fetchData } = useApiFetch()

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(literature, literatureConfig)

onMounted(async () => {
  try {
    const result = await fetchData({
      table: 'Literature',
      id: route.params.id,
    })
    
    // Check if the API returned an error response
    if (result.error === 'no entry found with the specified id') {
      router.push({
        path: '/error',
        query: { message: 'Literature not found' }
      })
    }
  } catch (err) {
    // Let the API fetch error handling take care of other errors
    console.error('Error fetching literature:', err)
  }
})
</script>
