<template>
  <BaseLegalLink
    :to="`/court-decision/${caseId}`"
    :class="props.class"
    :loading="loading"
    :error="error"
  >
    {{ caseId }}
  </BaseLegalLink>
</template>

<script setup>
import BaseLegalLink from '@/components/legal/BaseLegalLink.vue'
import { useLegalState } from '@/composables/useLegalState.js'

const props = defineProps({
  caseId: {
    type: String,
    required: true,
  },
  class: {
    type: String,
    default: '',
  },
})

const { loading, error } = useLegalState()
</script>
