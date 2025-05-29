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
      <section v-if="value" class="section-gap">
        <div>
          <span class="label" style="display: block; margin-bottom: 0.5rem">
            {{
              computedKeyLabelPairs.find((pair) => pair.key === 'Publication Title')?.label || 'Publication'
            }}
          </span>
          <span class="result-value-small">{{ value }}</span>
        </div>
      </section>
    </template>
    <template #publisher="{ value }">
      <section v-if="value" class="section-gap">
        <div>
          <span class="label" style="display: block; margin-bottom: 0.5rem">
            {{
              computedKeyLabelPairs.find((pair) => pair.key === 'Publisher')?.label || 'Publisher'
            }}
          </span>
          <span class="result-value-small">{{ value }}</span>
        </div>
      </section>
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
