<template>
  <div>
    <NuxtLink
      :to="`/court-decision/${caseId}`"
      :class="[
        'result-value-small',
        customClass,
        {
          'text-gray-500': loading,
          'text-red-500': error
        }
      ]"
    >
      <span v-if="loading">Loading...</span>
      <span v-else-if="error">{{ error }}</span>
      <span v-else>{{ caseId }}</span>
    </NuxtLink>
  </div>
</template>

<script setup>
const props = defineProps({
  caseId: {
    type: String,
    required: true
  },
  class: {
    type: String,
    default: ''
  }
})

const loading = ref(false)
const error = ref(null)
const customClass = computed(() => props.class || '')
</script>
