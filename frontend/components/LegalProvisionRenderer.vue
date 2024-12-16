<template>
  <div>
    <!-- Legal provision articles -->
    <div v-if="value && value.trim()">
      <div
        v-for="(item, itemIndex) in value.split(',')"
        :key="itemIndex"
        :class="valueClassMap['Legal provision articles'] || 'result-value'"
      >
        <NuxtLink
          :to="`/legal-instrument/${item.trim().split(' ')[0]}#${item.trim().split(' ').slice(1).join('')}`"
        >
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
        <NuxtLink
          :to="`/legal-instrument/${item.trim().split(' ')[0]}${item.trim().split(' ').slice(1).join('')}`"
        >
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
          fallbackData['More information'].length > 45
            ? 'result-value-small'
            : valueClassMap['Legal provision articles'] || 'result-value'
        "
      >
        {{ fallbackData['More information'].trim() }}
      </div>
    </div>

    <!-- Render N/A -->
    <div v-else>
      <span>N/A</span>
    </div>
  </div>
</template>

<script setup lang="ts">
//import { defineProps } from 'vue'

defineProps({
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
</script>
