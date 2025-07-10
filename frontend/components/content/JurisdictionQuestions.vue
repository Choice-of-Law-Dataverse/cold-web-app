<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <UCard class="cold-ucard">
          <div>
            <h2 class="mt-2 mb-8">
              Questions and Answers {{ jurisdictionName }}
              <InfoTooltip text="Questions" class="info-tooltip-small" />
            </h2>
            <!-- Desktop Table View -->
            <div class="table-full-width-wrapper hidden md:block">
              <UTable
                :rows="visibleRows"
                :columns="columns"
                :loading="loading || answersLoading"
                :progress="{ color: 'primary', animation: 'carousel' }"
              >
                <template #loading-state>
                  <div class="flex flex-col py-8 space-y-3 ml-8">
                    <LoadingBar />
                    <LoadingBar />
                    <LoadingBar />
                  </div>
                </template>
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
                    <NuxtLink
                      v-if="row.answer"
                      :to="row.answerLink"
                      class="result-value-small answer-link"
                    >
                      {{ row.answer }}
                    </NuxtLink>
                    <span v-else class="result-value-small">
                      {{ row.answer }}
                    </span>
                  </div>
                </template>
              </UTable>
            </div>

            <!-- Mobile Card View -->
            <div class="mobile-cards-wrapper block md:hidden">
              <div
                v-if="loading || answersLoading"
                class="flex flex-col py-8 space-y-3"
              >
                <LoadingBar />
                <LoadingBar />
                <LoadingBar />
              </div>
              <div v-else class="space-y-4">
                <div
                  v-for="row in visibleRows"
                  :key="row.id"
                  class="mobile-card"
                  :style="{ '--indent': `${row.level * 1}em` }"
                >
                  <div class="mobile-card-question">
                    <div class="flex items-start">
                      <span
                        v-if="row.hasExpand"
                        class="mr-2 cursor-pointer expand-icon-mobile"
                        @click.stop="toggleExpand(row)"
                        :style="{
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
                      <span
                        class="mobile-question-text"
                        style="white-space: pre-line"
                        >{{ row.question }}</span
                      >
                    </div>
                  </div>

                  <div class="mobile-card-details">
                    <div class="mobile-card-row" v-if="row.theme">
                      <div class="mobile-card-themes">
                        <span
                          v-for="theme in typeof row.theme === 'string'
                            ? row.theme.split(',')
                            : []"
                          :key="theme.trim()"
                          class="label-theme"
                        >
                          {{ theme.trim() }}
                        </span>
                      </div>
                    </div>

                    <div class="mobile-card-row" v-if="row.answer">
                      <div class="mobile-card-answer">
                        <NuxtLink
                          v-if="row.answer"
                          :to="row.answerLink"
                          class="result-value-small answer-link"
                        >
                          {{ row.answer }}
                        </NuxtLink>
                        <span v-else class="result-value-small">
                          {{ row.answer }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
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

import LoadingBar from '@/components/layout/LoadingBar.vue'

const {
  processedQuestionsData,
  loading,
  error,
  answersLoading,
  fetchQuestions,
} = useQuestions()

const attrs = useAttrs()
const jurisdictionName = computed(() => {
  const name = attrs.formattedJurisdiction?.[0] || ''
  return name ? `for ${name}` : ''
})

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
  width: 380px !important;
}
.table-full-width-wrapper td:nth-child(2),
.table-full-width-wrapper th:nth-child(2) {
  width: 35%;
  text-align: right !important;
}
.table-full-width-wrapper :deep(td:nth-child(3)),
.table-full-width-wrapper :deep(th:nth-child(3)) {
  width: 20%;
  min-width: 120px;
  max-width: 200px;
  text-align: right !important;
  padding-right: 2.5em !important;
  white-space: normal !important;
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
  line-height: 26px !important;
}

/* Responsive adjustments for smaller screens */
@media (max-width: 1024px) {
  .table-full-width-wrapper td:first-child,
  .table-full-width-wrapper th:first-child {
    width: 50% !important;
  }

  /* Stack theme labels vertically on tablet screens */
  .table-full-width-wrapper td:nth-child(2) div,
  .table-full-width-wrapper th:nth-child(2) div {
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-end !important;
    gap: 0.25rem !important;
  }

  .table-full-width-wrapper td:nth-child(2) .label-theme,
  .table-full-width-wrapper th:nth-child(2) .label-theme {
    margin-right: 0 !important;
    margin-bottom: 0.25rem !important;
  }
}

@media (max-width: 768px) {
  .table-full-width-wrapper td:first-child,
  .table-full-width-wrapper th:first-child {
    width: 45% !important;
  }
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
  margin-top: 1.45em;
}

.answer-link {
  text-decoration: none;
  color: var(--color-cold-purple) !important;
  font-weight: 600 !important;
}

.table-full-width-wrapper :deep(.mb-2\.5) {
  margin-bottom: 0 !important;
}

.table-full-width-wrapper :deep(.h-2) {
  height: 16px !important;
  min-height: 16px !important;
}

/* Mobile responsive styles */
.mobile-cards-wrapper {
  margin-left: calc(-1 * var(--card-padding, 1.5rem));
  margin-right: calc(-1 * var(--card-padding, 1.5rem));
  width: calc(100% + 2 * var(--card-padding, 1.5rem));
  margin-bottom: -1.55rem !important;
  padding: 0 var(--card-padding, 1.5rem);
}

.mobile-card {
  border-bottom: 1px solid var(--color-cold-gray);
  padding: 1.5rem 0;
  margin-left: var(--indent);
}

.mobile-card:last-child {
  border-bottom: none;
}

.mobile-card-question {
  margin-bottom: 1rem;
}

.mobile-question-text {
  display: block;
  width: 100%;
  word-break: break-word;
  font-size: 14px !important;
  line-height: 26px !important;
  /* color: var(--color-cold-night) !important; */
  /* line-height: 1.6 !important; */
  /* font-size: 0.95rem; */
}

.expand-icon-mobile {
  display: inline-flex;
  align-items: flex-start;
  margin-top: 0.2rem;
  cursor: pointer;
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.mobile-card-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.mobile-card-row {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.mobile-card-row:last-child {
  margin-bottom: 0;
}

.mobile-card-themes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.mobile-card-themes .label-theme {
  margin-right: 0 !important;
}

.mobile-card-answer {
  color: var(--color-cold-night) !important;
  line-height: 1.6 !important;
}

/* Ensure themes and answers are properly styled on mobile */
@media (max-width: 767px) {
  .answer-link {
    word-break: break-word;
  }
}
</style>
