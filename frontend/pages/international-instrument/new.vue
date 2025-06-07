<template>
  <BaseDetailLayout
    :loading="false"
    :resultData="{}"
    :keyLabelPairs="[]"
    :valueClassMap="{}"
    sourceTable="International Instrument"
    :hideBackButton="true"
    headerMode="new"
  >
    <!-- Blank layout for new international instrument -->
  </BaseDetailLayout>
</template>

<script setup>
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
// No logic for now
</script>

<style scoped>
/* Hide the back button and all right-side card header buttons */
:deep(.back-to-results),
:deep(.card-header__actions),
:deep(.card-header [class*='actions']) {
  display: none !important;
}
</style>
