<template>
  <div>
    <NuxtLink
      :to="to"
      :class="[
        baseClass,
        customClass,
        {
          'text-gray-500': loading,
          'text-red-500': error
        }
      ]"
    >
      <span v-if="loading">Loading...</span>
      <span v-else-if="error">{{ error }}</span>
      <span v-else><slot /></span>
    </NuxtLink>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  to: {
    type: String,
    required: true
  },
  class: {
    type: String,
    default: ''
  },
  baseClass: {
    type: String,
    default: 'result-value-small'
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  }
})

const customClass = computed(() => props.class || '')
</script> 