<template>
  <div>
    <!-- Legal provision articles -->
    <div v-if="value && value.trim()">
      <div
        v-for="(item, itemIndex) in value.split(',')"
        :key="itemIndex"
        :class="valueClassMap['Legal provision articles'] || 'result-value'"
      >
        <NuxtLink :to="generateLegalProvisionLink(item)">
          {{ item.trim() }}
        </NuxtLink>
      </div>
    </div>

    <!-- Fallback to Legislation-ID -->
    <div
      v-else-if="
        fallbackData['Legislation-ID'] && fallbackData['Legislation-ID'].trim()
      "
    >
      <div
        v-for="(item, itemIndex) in fallbackData['Legislation-ID'].split(',')"
        :key="itemIndex"
        :class="valueClassMap['Legal provision articles'] || 'result-value'"
      >
        <NuxtLink :to="generateLegalProvisionLink(item)">
          {{ item.trim() }}
        </NuxtLink>
      </div>
    </div>

    <!-- Fallback to More information -->
    <div
      v-else-if="
        fallbackData['More information'] &&
        fallbackData['More information'].trim()
      "
    >
      <div
        :class="
          getProvisionClass(
            fallbackData['More information'],
            valueClassMap['Legal provision articles'] || 'result-value'
          )
        "
      >
        {{
          fallbackData['More information']
            .replace(/\n/g, ' ') // Remove line breaks
            .trim()
        }}
      </div>
    </div>

    <!-- Render N/A -->
    <div v-else>
      <span>N/A</span>
    </div>
  </div>
</template>

<script setup>
import { generateLegalProvisionLink, getProvisionClass } from '~/utils/legal'

defineProps({
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
</script> 