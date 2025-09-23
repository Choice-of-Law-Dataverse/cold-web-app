<template>
  <BaseLegalRenderer
    :items="value"
    :value-class-map="valueClassMap"
    :empty-value-behavior="emptyValueBehavior"
    default-class="result-value-small"
  >
    <template #default="{ item }">
      <NuxtLink :to="generateCourtDecisionLink(item)">
        <template v-if="caseTitles[item] !== undefined">
          {{ caseTitles[item] }}
        </template>
        <template v-else>
          <LoadingBar />
        </template>
      </NuxtLink>
    </template>
  </BaseLegalRenderer>
</template>

<script setup>
import { computed } from 'vue'
import { useRecordDetailsList } from '@/composables/useRecordDetails'
import BaseLegalRenderer from './BaseLegalRenderer.vue'
import { NuxtLink } from '#components'
import LoadingBar from '@/components/layout/LoadingBar.vue'

const props = defineProps({
  value: {
    type: [Array, String],
    default: () => [],
  },
  valueClassMap: {
    type: String,
    default: '',
  },
})

const excludedValues = new Set(['na', 'not found', 'n/a'])

// Compute unique IDs and fetch titles via composable
const decisionIds = computed(() => {
  const items = Array.isArray(props.value) ? props.value : [props.value]
  const filtered = items.filter(Boolean)
  const unique = [...new Set(filtered)]
  return unique
})

const { data: decisions } = useRecordDetailsList(
  computed(() => 'Court Decisions'),
  decisionIds
)

const caseTitles = computed(() => {
  const map = {}
  if (!decisions.value) return map

  decisions.value.forEach((rec) => {
    if (!rec) return
    const options = [rec['Case Title'], rec['Case Citation'], rec.id]
    map[rec.id] = options.filter(
      (t) => t && !excludedValues.has(t.toLowerCase())
    )[0]
  })
  return map
})

// Helper to generate the link URL for a court decision.
function generateCourtDecisionLink(caseId) {
  return `/court-decision/${caseId}`
}
</script>
