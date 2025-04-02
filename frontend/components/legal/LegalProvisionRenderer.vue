<template>
  <BaseLegalRenderer
    :items="provisionItems"
    :valueClassMap="valueClassMap['Legal provision articles']"
    defaultClass="result-value"
  >
    <template #default="{ item }">
      <NuxtLink :to="generateLegalProvisionLink(item)">
        {{ item.trim() }}
      </NuxtLink>
    </template>
  </BaseLegalRenderer>
</template>

<script setup>
import { computed } from 'vue'
import { generateLegalProvisionLink } from '~/utils/legal'
import BaseLegalRenderer from './BaseLegalRenderer.vue'

const props = defineProps({
  value: {
    type: String,
    default: ''
  },
  fallbackData: {
    type: Object,
    required: true
  },
  valueClassMap: {
    type: Object,
    default: () => ({})
  }
})

const provisionItems = computed(() => {
  if (props.value && props.value.trim()) {
    return props.value.split(',')
  }
  if (props.fallbackData['Legislation-ID'] && props.fallbackData['Legislation-ID'].trim()) {
    return props.fallbackData['Legislation-ID'].split(',')
  }
  if (props.fallbackData['More information'] && props.fallbackData['More information'].trim()) {
    return [props.fallbackData['More information'].replace(/\n/g, ' ').trim()]
  }
  return []
})
</script> 