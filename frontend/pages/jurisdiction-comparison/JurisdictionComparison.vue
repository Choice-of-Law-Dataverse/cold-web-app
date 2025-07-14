<template>
  <BaseDetailLayout
    :loading="false"
    :resultData="{}"
    :keyLabelPairs="[]"
    :valueClassMap="{}"
    sourceTable=""
  >
    <JCOverview />
  </BaseDetailLayout>
</template>

<script setup>
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import JCOverview from './JCOverview.vue'
</script>
