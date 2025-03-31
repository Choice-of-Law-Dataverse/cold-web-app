<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="literature"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Literature"
  />
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import { useApiFetch } from '~/composables/useApiFetch'
import { useDetailDisplay } from '~/composables/useDetailDisplay'

const route = useRoute()

const { loading, error, data: literature, fetchData } = useApiFetch()

// Define the keys and labels for dynamic rendering
const keyLabelPairs = [
  { key: 'Title', label: 'Title' },
  { key: 'Author', label: 'Author' },
  { key: 'Editor', label: 'Editor' },
  { key: 'Publication Year', label: 'Year' },
  { key: 'Publication Title', label: 'Publication' },
]

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(literature, keyLabelPairs)

onMounted(() => {
  fetchData({
    table: 'Literature',
    id: route.params.id,
  })
})
</script>
