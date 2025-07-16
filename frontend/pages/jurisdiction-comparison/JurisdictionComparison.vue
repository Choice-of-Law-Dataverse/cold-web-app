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
      <div class="px-6 py-4">
        <JCMainQuestions />
      </div>
    </template>
  </BaseDetailLayout>
</template>

<script setup>
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import JCOverview from '@/pages/jurisdiction-comparison/JCOverview.vue'
import JCMainQuestions from '@/pages/jurisdiction-comparison/JCMainQuestions.vue'
</script>
