<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <BaseDetailLayout
        :loading="false"
        :resultData="{}"
        :keyLabelPairs="[]"
        :valueClassMap="{}"
        sourceTable=""
      >
        <JCOverview />
      </BaseDetailLayout>
    </div>
  </main>
</template>

<script setup>
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import JCOverview from './JCOverview.vue'
</script>
