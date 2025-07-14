<template>
  <BaseDetailLayout
    :loading="false"
    :resultData="{}"
    :keyLabelPairs="[]"
    :valueClassMap="{}"
    sourceTable=""
  >
    <template #full-width>
      <div class="px-6 py-4">
        <JCOverview />
      </div>
    </template>
  </BaseDetailLayout>
</template>

<script setup>
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import JCOverview from './JCOverview.vue'
</script>
