<template>
  <div>
    <!-- Render legal provisions inline to avoid nested lists -->
    <template v-for="(item, index) in provisionItems" :key="index">
      <NuxtLink :to="generateLegalProvisionLink(item)">
        {{ item.trim() }}
      </NuxtLink>
      <span v-if="index !== provisionItems.length - 1">, </span>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { generateLegalProvisionLink } from '~/utils/legal'

const props = defineProps({
  value: {
    type: String,
    default: '',
  },
  fallbackData: {
    type: Object,
    required: true,
  },
  valueClassMap: {
    type: Object,
    default: () => ({}),
  },
})

const provisionItems = computed(() => {
  if (props.value && props.value.trim()) {
    return props.value.split(',')
  }
  if (
    props.fallbackData['Legislation-ID'] &&
    props.fallbackData['Legislation-ID'].trim()
  ) {
    return props.fallbackData['Legislation-ID'].split(',')
  }
  if (
    props.fallbackData['More information'] &&
    props.fallbackData['More information'].trim()
  ) {
    return [props.fallbackData['More information'].replace(/\n/g, ' ').trim()]
  }
  return []
})
</script>
