<template>
  <div v-if="shouldDisplay" class="mt-12">
    <span v-if="label" class="label">{{ label }}</span>
    <InfoTooltip v-if="tooltip" :text="tooltip" />
    <ul v-if="questionList.length">
      <li v-for="(q, idx) in questionList" :key="idx">
        <NuxtLink :to="`/question/${jurisdictionCode}_${q}`">
          {{ questionLabels[idx] || jurisdictionCode + '_' + q }}
        </NuxtLink>
      </li>
    </ul>
    <span v-else>No related questions.</span>
  </div>
</template>

<script setup>
import { computed, toRefs, ref, watchEffect } from 'vue'
import { useRuntimeConfig } from '#imports'
import InfoTooltip from '@/components/ui/InfoTooltip.vue'

const props = defineProps({
  label: { type: String, default: 'Related Questions' },
  jurisdictionCode: { type: String, default: '' },
  questions: { type: String, default: '' },
  emptyValueBehavior: { type: Object, default: () => ({ action: 'hide' }) },
  tooltip: { type: String, default: '' },
})

const { jurisdictionCode, questions, emptyValueBehavior } = toRefs(props)
const config = useRuntimeConfig()

const questionList = computed(() =>
  questions.value
    ? questions.value
        .split(',')
        .map((q) => q.trim())
        .filter((q) => q)
    : []
)

const shouldDisplay = computed(() => {
  if (
    emptyValueBehavior.value?.action === 'hide' &&
    questionList.value.length === 0
  ) {
    return false
  }
  return true
})

const questionLabels = ref([])

watchEffect(async () => {
  // Only fetch if there are questions and a jurisdiction code
  if (!jurisdictionCode.value || !questionList.value.length) {
    questionLabels.value = []
    return
  }
  // Fetch all question labels in parallel
  const results = await Promise.all(
    questionList.value.map(async (q) => {
      try {
        const response = await fetch(
          `/api/proxy/search/details`,
          {
            method: 'POST',
            headers: {
              authorization: `Bearer ${config.public.FASTAPI}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              table: 'Answers',
              id: `${jurisdictionCode.value}_${q}`,
            }),
          }
        )
        const data = await response.json()
        return data.Question || `${jurisdictionCode.value}_${q}`
      } catch (e) {
        return `${jurisdictionCode.value}_${q}`
      }
    })
  )
  questionLabels.value = results
})
</script>
