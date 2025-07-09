<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <UCard class="cold-ucard">
          <div>
            <h2 class="mt-2 mb-8">
              Questions and Answers for {{ jurisdictionName }}
              <InfoTooltip text="Questions" class="info-tooltip-small" />
            </h2>
            <div class="table-full-width-wrapper">
              <UTable :rows="visibleRows" :columns="columns">
                <template #question-data="{ row }">
                  <div
                    class="result-value-small question-indent"
                    :style="{ '--indent': `${row.level * 2}em` }"
                    style="display: flex; align-items: flex-start"
                  >
                    <span
                      v-if="row.hasExpand"
                      class="mr-1 align-middle cursor-pointer mt-1 expand-icon"
                      @click.stop="toggleExpand(row)"
                      :style="{
                        display: 'inline-flex',
                        alignItems: 'center',
                        transform: row.expanded
                          ? 'rotate(90deg)'
                          : 'rotate(0deg)',
                      }"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        width="16"
                        height="16"
                        fill="none"
                        style="color: var(--color-cold-purple)"
                      >
                        <path
                          d="M9 6l6 6-6 6"
                          stroke="currentColor"
                          stroke-width="3"
                          stroke-linecap="square"
                          stroke-linejoin="square"
                        />
                      </svg>
                    </span>
                    <span class="question-text" style="white-space: pre-line">{{
                      row.question
                    }}</span>
                  </div>
                </template>
                <template #theme-data="{ row }">
                  <div style="text-align: right">
                    <span
                      v-for="theme in typeof row.theme === 'string'
                        ? row.theme.split(',')
                        : []"
                      :key="theme.trim()"
                      class="label-theme"
                      style="margin-right: 12px"
                    >
                      {{ theme.trim() }}
                    </span>
                  </div>
                </template>
                <template #answer-data="{ row }">
                  <div style="text-align: right">
                    <span class="result-value-small">
                      {{ row.answer }}
                    </span>
                  </div>
                </template>
              </UTable>
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted, useAttrs } from 'vue'
import { useQuestions } from '@/composables/useQuestions'
import InfoTooltip from '@/components/ui/InfoTooltip.vue'

// const { questions, loading, error, fetchQuestions } = useQuestions()
const { processedQuestionsData, loading, error, fetchQuestions } =
  useQuestions()

const attrs = useAttrs()
const jurisdictionName = computed(() => attrs.formattedJurisdiction?.[0] || '')

onMounted(async () => {
  await fetchQuestions()
})

// Use a ref so we can mutate expanded state reactively
const rows = ref([])

onMounted(async () => {
  await fetchQuestions()
  // Deep clone processedQuestionsData so each row is a unique object
  rows.value = processedQuestionsData.value.map((row) => ({ ...row }))
})

const columns = [
  { key: 'question', label: 'Question' },
  { key: 'theme', label: 'Theme' },
  { key: 'answer', label: 'Answer' },
]

// Compute visible rows based on expanded state
// const visibleRows = computed(() => rows.value)

const visibleRows = computed(() => {
  const result = []
  const parentExpanded = {}

  for (const row of rows.value) {
    // Always show top-level rows
    if (row.level === 0) {
      result.push(row)
      parentExpanded[row.id] = row.expanded
    } else {
      // Show child if its parent is expanded
      if (parentExpanded[row.parentId]) {
        result.push(row)
        parentExpanded[row.id] = row.expanded
      }
    }
  }
  return result
})

function toggleExpand(row) {
  row.expanded = !row.expanded
  if (!row.expanded) {
    // Recursively collapse all descendants
    collapseDescendants(row.id)
  }
}

function collapseDescendants(parentId) {
  for (const child of rows.value) {
    if (child.parentId === parentId) {
      if (child.hasExpand) {
        child.expanded = false
        collapseDescendants(child.id)
      }
    }
  }
}
</script>

<style scoped>
.result-value-small,
.result-value-small td,
.result-value-small th,
.result-value-small tr,
.result-value-small span,
.result-value-small div {
  color: var(--color-cold-night) !important;
  line-height: 26px !important;
}

.table-full-width-wrapper {
  margin-left: calc(-1 * var(--card-padding, 1.5rem));
  margin-right: calc(-1 * var(--card-padding, 1.5rem));
  width: calc(100% + 2 * var(--card-padding, 1.5rem));
  margin-bottom: -1.55rem !important;
}
.table-full-width-wrapper table {
  width: 100% !important;
  table-layout: auto;
  table-layout: fixed;
}

.table-full-width-wrapper td,
.table-full-width-wrapper th {
  white-space: normal !important;
  word-break: break-word !important;
  overflow-wrap: break-word !important;
}

.table-full-width-wrapper :deep(tr) {
  height: 80px !important;
  min-height: 80px !important;
}

.table-full-width-wrapper tr[aria-expanded='true'],
.table-full-width-wrapper tr.is-expanded,
.table-full-width-wrapper tr.expanded,
.table-full-width-wrapper tr[aria-selected='true'],
.table-full-width-wrapper .bg-gray-50,
.table-full-width-wrapper .bg-gray-100,
.table-full-width-wrapper .bg-gray-200 {
  background-color: white !important;
}

.table-full-width-wrapper :deep(thead) {
  display: none;
}

.table-full-width-wrapper :deep(th),
.table-full-width-wrapper :deep(td) {
  border-bottom: 1px solid var(--color-cold-gray) !important;
  border-top: 1px solid var(--color-cold-gray) !important;
  border-left: 0px;
  border-right: 0px;
}

.table-full-width-wrapper td:first-child,
.table-full-width-wrapper th:first-child {
  width: 50% !important;
}
.table-full-width-wrapper td:nth-child(2),
.table-full-width-wrapper th:nth-child(2) {
  width: 40%;
  text-align: right !important;
}
.table-full-width-wrapper :deep(td:nth-child(3)),
.table-full-width-wrapper :deep(th:nth-child(3)) {
  width: 10%;
  text-align: right !important;
  padding-right: 2.5em !important;
}

.info-tooltip-small {
  font-size: 0.75em !important;
}
.question-indent {
  padding-left: var(--indent);
}
.question-text {
  /* Ensures text wraps and all lines are indented */
  display: block;
  width: 100%;
  word-break: break-word;
  padding-top: 1.1em;
}
.expand-icon {
  display: inline-flex;
  align-items: center;
  margin-right: 0.5em;
  cursor: pointer;
  /* Optional: tweak vertical alignment */
  margin-top: 1.4em;
}
</style>
