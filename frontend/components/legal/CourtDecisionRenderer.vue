<template>
  <BaseLegalRenderer
    :items="value"
    :valueClassMap="valueClassMap"
    defaultClass="result-value-small"
  >
    <template #default="{ item }">
      <CourtDecisionLink :caseId="item" />
    </template>
  </BaseLegalRenderer>
</template>

<script setup>
import CourtDecisionLink from './CourtDecisionLink.vue'
import BaseLegalRenderer from './BaseLegalRenderer.vue'

defineProps({
  value: {
    type: [Array, String],
    default: () => []
  },
  valueClassMap: {
    type: String,
    default: ''
  }
})
</script> 