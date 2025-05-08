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
      <div
        v-if="value && literature['Item Type'] !== 'book'"
        class="field-container publication-field"
      >
        <p class="label field-label">Publication</p>
        <p class="result-value-small field-value">
          {{ value }}
        </p>
      </div>
    </template>
    <template #publisher="{ value }">
      <div
        v-if="value && literature['Item Type'] === 'book'"
        class="field-container publisher-field"
      >
        <p class="label field-label">Publisher</p>
        <p class="result-value-small field-value">
          {{ value }}
        </p>
      </div>
    </template>
    <template #url="{ value }">
      <div
        v-if="!literature['Open Access URL'] && value"
        class="field-container url-field"
      >
        <p class="label field-label">Link</p>
        <p class="result-value-small field-value">
          <a :href="value" target="_blank" rel="noopener noreferrer">
            {{ value }}
          </a>
        </p>
      </div>
    </template>
    <template #open-access-url="{ value }">
      <div v-if="value" class="field-container url-field">
        <p class="label field-label">Open Access URL</p>
        <p class="result-value-small field-value">
          <a :href="value" target="_blank" rel="noopener noreferrer">
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

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  literature,
  literatureConfig
)

onMounted(async () => {
  try {
    const result = await fetchData({
      table: 'Literature',
      id: route.params.id,
    })
    // Check if result is null or an empty object
    if (!result || Object.keys(result).length === 0) {
      throw { isNotFound: true, table: 'Literature' }
    }
  } catch (err) {
    if (err.isNotFound) {
      router.push({
        path: '/error',
        query: { message: `${err.table} not found` },
      })
    } else {
      console.error('Error fetching literature:', err)
    }
  }
})
</script>

<style scoped>
/* Adjust these values to change spacing consistently */
.field-container {
  /* default container style for fields */
}
.publication-field {
  /* margin-top: -0.5rem; equivalent to -mt-2 */
  margin-bottom: 1rem;
}
.publisher-field {
  margin-bottom: 1.5rem;
}
.url-field {
  padding-top: 1rem; /* equivalent to !pt-2 */
  margin-bottom: 1.5rem;
}
.field-label {
  margin-bottom: 1rem;
}
.field-value {
  margin-bottom: 1rem;
}
</style>
