<template>
  <ResultCard :resultData="resultData" cardType="Court decisions">
    <div v-for="key in courtDecisionKeys" :key="key">
      <div class="label-key">{{ keyMap[key] }}</div>
      <div
        :class="[
          valueClassMap[key] || 'result-value', // Use the mapped class or a default class
        ]"
      >
        <!-- Customize content display based on the key, if needed -->
        <template v-if="key === 'Choice of law issue'">
          {{ resultData[key] || '[Missing Information]' }}
        </template>
        <template v-else>
          <span>{{ resultData[key] }}</span>
        </template>
      </div>
    </div>
  </ResultCard>
</template>

<script setup>
// Props
const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
})

// Define the keys and mappings specific to court decisions
const courtDecisionKeys = ['Case', 'Choice of law issue']
const keyMap = {
  Case: 'Case Title',
  'Choice of law issue': 'Choice of Law Issue',
}

// Map different CSS styles to different typographic components
const valueClassMap = {
  Case: 'result-value-medium',
  'Choice of law issue': 'result-value-small',
}
</script>
