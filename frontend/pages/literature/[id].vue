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
  </BaseDetailLayout>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import { useApiFetch } from '~/composables/useApiFetch'
import { useDetailDisplay } from '~/composables/useDetailDisplay'
import BaseCardHeader from '~/components/ui/BaseCardHeader.vue'
import { literatureConfig } from '~/config/pageConfigs'

const route = useRoute()

const { loading, error, data: literature, fetchData } = useApiFetch()

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(literature, literatureConfig)

onMounted(() => {
  fetchData({
    table: 'Literature',
    id: route.params.id,
  })
})
</script>
