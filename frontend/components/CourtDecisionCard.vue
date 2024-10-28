<template>
  <ResultCard :resultData="resultData" cardType="Court decisions">
    <div v-for="key in courtDecisionKeys" :key="key">
      <div class="result-key">{{ keyMap[key] }}</div>
      <div class="result-value">
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
  Case: 'CASE TITLE',
  'Jurisdiction Names': 'JURISDICTION',
  'Choice of law issue': 'CHOICE OF LAW ISSUE',
}
</script>
