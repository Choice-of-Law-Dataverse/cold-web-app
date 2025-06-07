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
    <!-- Always render this section, even if keyLabelPairs is empty -->
    <div class="section-gap p-0 m-0">
      <p class="label mb-2">Name</p>
      <UInput v-model="name" placeholder="Enter name..." />
    </div>
  </BaseDetailLayout>
</template>

<script setup>
import { ref } from 'vue'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
const name = ref('')
</script>

<style scoped>
/* Hide the back button and all right-side card header buttons */
:deep(.back-to-results),
:deep(.card-header__actions),
:deep(.card-header [class*='actions']) {
  display: none !important;
}
</style>
