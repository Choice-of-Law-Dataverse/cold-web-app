<template>
  <ResultCard :resultData="resultData" cardType="Legislation">
    <div v-for="key in legislationKeys" :key="key">
      <div class="label-key">{{ keyMap[key] }}</div>
      <div
        :class="[
          valueClassMap[key] || 'result-value', // Use the mapped class or a default class
        ]"
      >
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
  'Title (in English)': 'Title',
  Abbreviation: 'Abbreviation',
}

// Map different CSS styles to different typographic components
const valueClassMap = {
  'Title (in English)': 'result-value-small',
  Abbreviation: 'result-value-medium',
}
</script>
