<template>
  <ResultCard :resultData="resultData" cardType="Answers">
    <div v-for="(key, index) in answerKeys" :key="key">
      <div class="label-key">{{ keyMap[key] }}</div>
      <div
        :class="[
          'result-value',
          { 'no-margin': index === answerKeys.length - 1 },
        ]"
      >
        <!-- Specific handling for 'Legal provision articles' -->
        <template v-if="key === 'Legal provision articles'">
          <div v-if="resultData[key]">
            <span
              v-for="(item, itemIndex) in resultData[key].split(',')"
              :key="itemIndex"
              style="margin-right: 10px"
            >
              <NuxtLink
                :to="`/legal-instrument/${item.trim().split(' ')[0]}#${item.trim().split(' ').slice(1).join('')}`"
              >
                {{ item.trim() }}
              </NuxtLink>
            </span>
          </div>
          <div v-else>No legal provision</div>
        </template>

        <!-- Default handling for other keys -->
        <template v-else>
          {{ resultData[key] }}
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

// Define the keys and mappings specific to answer results
const answerKeys = ['Questions', 'Answer', 'Legal provision articles']
const keyMap = {
  Answer: 'ANSWER',
  Questions: 'QUESTION',
  'Legal provision articles': 'SOURCE',
}
</script>
