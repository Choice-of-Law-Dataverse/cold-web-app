<template>
  <!-- Use the shared detail layout to match spacing, container width, and card styling. -->
  <!-- Use sourceTable="Loading" so the header stays hidden, yielding a clean blank card. -->
  <BaseDetailLayout
    :loading="loading"
    :resultData="resultData"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Loading"
  >
    <h1 class="mb-12">Arbitral Awards</h1>
  </BaseDetailLayout>
</template>

<script setup lang="ts">
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'

useHead({
  title: 'Arbitral Awards — CoLD',
})

// Minimal props for BaseDetailLayout to render a blank card with the same layout
const loading = false
const resultData = {} as any
const computedKeyLabelPairs: any[] = []
const valueClassMap: Record<string, string> = {}
</script>
