<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="literature"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Literature"
  >
    <template #publication-title="{ value }">
      <section v-if="value" class="section-gap">
        <div>
          <span class="label" style="display: block; margin-bottom: 0.5rem">
            {{
              computedKeyLabelPairs.find(
                (pair) => pair.key === 'Publication Title'
              )?.label || 'Publication'
            }}
            <InfoTooltip
              v-if="
                computedKeyLabelPairs.find(
                  (pair) => pair.key === 'Publication Title'
                )?.tooltip
              "
              :text="
                computedKeyLabelPairs.find(
                  (pair) => pair.key === 'Publication Title'
                )?.tooltip
              "
            />
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
              computedKeyLabelPairs.find((pair) => pair.key === 'Publisher')
                ?.label || 'Publisher'
            }}
            <InfoTooltip
              v-if="
                computedKeyLabelPairs.find((pair) => pair.key === 'Publisher')
                  ?.tooltip
              "
              :text="
                computedKeyLabelPairs.find((pair) => pair.key === 'Publisher')
                  ?.tooltip
              "
            />
          </span>
          <span class="result-value-small">{{ value }}</span>
        </div>
      </section>
    </template>
  </BaseDetailLayout>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import { useApiFetch } from '@/composables/useApiFetch'
import { useDetailDisplay } from '@/composables/useDetailDisplay'
import InfoTooltip from '@/components/ui/InfoTooltip.vue'
import { literatureConfig } from '@/config/pageConfigs'
import { useHead } from '#imports'

const route = useRoute()
const router = useRouter()

const { loading, error, data: literature, fetchData } = useApiFetch()

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  literature,
  literatureConfig
)

// Set dynamic page title based on 'Title'
watch(
  literature,
  (newVal) => {
    if (!newVal) return
    const title = newVal['Title']
    const pageTitle =
      title && title.trim() ? `${title} — CoLD` : 'Literature — CoLD'
    useHead({
      title: pageTitle,
      link: [
        {
          rel: 'canonical',
          href: `https://cold.global${route.fullPath}`,
        },
      ],
      meta: [
        {
          name: 'description',
          content: pageTitle,
        },
      ],
    })
  },
  { immediate: true }
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
