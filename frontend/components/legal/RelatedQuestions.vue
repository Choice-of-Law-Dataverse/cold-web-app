<template>
  <div>
    <span v-if="label" class="label">{{ label }}</span>
    <ul v-if="questionList.length">
      <li v-for="(q, idx) in questionList" :key="idx">
        {{ jurisdictionCode }}_{{ q.trim() }}
      </li>
    </ul>
    <span v-else>No related questions.</span>
  </div>
</template>

<script setup>
import { computed, toRefs } from 'vue'

const props = defineProps({
  label: { type: String, default: 'Related Questions' },
  jurisdictionCode: { type: String, default: '' },
  questions: { type: String, default: '' },
})

const { jurisdictionCode, questions } = toRefs(props)

const questionList = computed(() =>
  questions.value
    ? questions.value
        .split(',')
        .map((q) => q.trim())
        .filter((q) => q)
    : []
)
</script>
