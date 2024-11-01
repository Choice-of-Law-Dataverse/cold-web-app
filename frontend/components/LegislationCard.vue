<template>
  <ResultCard :resultData="resultData" cardType="Legislation">
    <div v-for="key in legislationKeys" :key="key">
      <div class="label-key">{{ keyMap[key] }}</div>
      <div class="result-value">
        {{ resultData[key] || '[Missing Information]' }}
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

const legislationKeys = ['Abbreviation', 'Title (in English)']

const keyMap = {
  // Legislations
  'Title (in English)': 'TITLE',
  'Jurisdiction name': 'JURISDICTION',
  Abbreviation: 'Abbreviation',
}
</script>
