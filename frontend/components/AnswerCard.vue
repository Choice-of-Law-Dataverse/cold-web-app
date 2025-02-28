<template>
  <ResultCard :resultData="resultData" cardType="Answers">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
      <!-- Question in the 1st column -->
      <div class="md:col-span-4">
        <div class="label-key">{{ keyMap.Question }}</div>
        <div :class="valueClassMap.Question || 'result-value'">
          {{ resultData.Question }}
        </div>
      </div>

      <!-- Answer in the 6th column -->
      <div class="md:col-start-6 md:col-span-2">
        <div class="label-key">{{ keyMap.Answer }}</div>
        <div :class="getAnswerClass(resultData.Answer)">
          {{ resultData.Answer }}
        </div>
      </div>

      <!-- Source in the 8th column -->
      <div
        v-if="resultData.Answer !== 'No data'"
        class="md:col-start-8 md:col-span-4"
      >
        <div class="label-key">{{ keyMap['Legal provision articles'] }}</div>
        <QuestionSourceList
          :sources="
            [
              resultData['Legal provision articles'] ||
                resultData['Legislation-ID'], // ||
            ].filter(Boolean)
          "
          :fallbackData="resultData"
          :valueClassMap="valueClassMap"
          :noLinkList="[resultData['More Information']]"
          :fetchPrimarySource="true"
          :fetchOupChapter="true"
        />
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

// Define the keys and mappings specific to answer results
const answerKeys = ['Question', 'Answer', 'Legal provision articles']

const keyMap = {
  Answer: 'Answer',
  Question: 'Question',
  'Legal provision articles': 'Source',
}

// Map different CSS styles to different typographic components
const valueClassMap = {
  //Answer: 'result-value-large',
  Question: 'result-value-medium',
  'Legal provision articles': 'result-value-small',
}
const getAnswerClass = (answer) => {
  return answer === 'Yes' || answer === 'No'
    ? 'result-value-large'
    : 'result-value-medium'
}
</script>

<style scoped>
.answer-card-grid {
  display: grid;
  grid-template-columns: repeat(12, var(--column-width));
  column-gap: var(--gutter-width);
  align-items: start;
}

.grid-item {
  display: flex;
  flex-direction: column;
}

.label-key {
  @extend .label;
  padding: 0;
  margin-top: 12px;
}
</style>
