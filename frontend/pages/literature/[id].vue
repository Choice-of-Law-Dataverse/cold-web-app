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
      <div v-if="value">
        <p class="label-key -mb-1">Publication</p>
        <p class="result-value-small">
          {{ value }}
        </p>
      </div>
    </template>
    <template #publisher="{ value }">
      <div v-if="value">
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
import { onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import { useApiFetch } from '~/composables/useApiFetch'
import { useDetailDisplay } from '~/composables/useDetailDisplay'
import BaseCardHeader from '~/components/ui/BaseCardHeader.vue'
import { literatureConfig } from '~/config/pageConfigs'

const route = useRoute()

const { loading, error, data: literature, fetchData } = useApiFetch()

// Modify the literature data to handle the conditional display
const modifiedLiterature = computed(() => {
  if (!literature.value) return null
  
  const isBook = literature.value['Item Type'] === 'book'
  
  return {
    ...literature.value,
    'Publication Title': isBook ? null : literature.value['Publication Title'],
    'Publisher': isBook ? literature.value['Publisher'] : null
  }
})

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(modifiedLiterature, literatureConfig)

onMounted(() => {
  fetchData({
    table: 'Literature',
    id: route.params.id,
  })
})
</script>
