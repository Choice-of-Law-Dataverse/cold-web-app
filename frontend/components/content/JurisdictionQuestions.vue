<template>
  <UCard class="cold-ucard">
    <div class="overflow-hidden">
      <h2 class="mb-8 mt-2">Questions and Answers {{ jurisdictionName }}</h2>
      <!-- Desktop Table View -->
      <div class="table-full-width-wrapper hidden md:block">
        <UTable
          :rows="visibleRows"
          :columns="columns"
          :loading="loading || answersLoading"
          :progress="{ color: 'primary', animation: 'carousel' }"
        >
          <template #loading-state>
            <div class="ml-8 flex flex-col space-y-3 py-8">
              <LoadingBar />
              <LoadingBar />
              <LoadingBar />
            </div>
          </template>
          <template #question-data="{ row }">
            <div
              :id="`question-${row.id}`"
              class="result-value-small question-indent"
              :style="{ '--indent': `${row.level * 2}em` }"
              style="display: flex; align-items: flex-start"
            >
              <span class="question-text whitespace-pre-line">{{
                row.question
              }}</span>
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
          class="flex flex-col space-y-3 py-8"
        >
          <LoadingBar />
          <LoadingBar />
          <LoadingBar />
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="row in visibleRows"
            :id="`question-${row.id}`"
            :key="row.id"
            class="mobile-card"
            :style="{ '--indent': `${row.level * 1}em` }"
          >
            <div class="mobile-card-question">
              <div class="flex items-start">
                <span class="mobile-question-text whitespace-pre-line">{{
                  row.question
                }}</span>
              </div>
            </div>

            <div v-if="row.answer" class="mobile-card-details">
              <div class="mobile-card-row">
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
</template>

<script setup>
import { computed, useAttrs } from "vue";
import { useRoute } from "vue-router";
import { useQuestionsWithAnswers } from "@/composables/useQuestionsWithAnswers";
import LoadingBar from "@/components/layout/LoadingBar.vue";

const route = useRoute();

const {
  data: questionWithAnswersData,
  loading,
  answersLoading,
} = useQuestionsWithAnswers(computed(() => route?.params?.id));

const attrs = useAttrs();
const jurisdictionName = computed(() => {
  const name = attrs.formattedJurisdiction?.[0] || "";
  return name ? `for ${name}` : "";
});

const rows = computed(() => {
  if (
    !questionWithAnswersData.value ||
    !Array.isArray(questionWithAnswersData.value)
  ) {
    return [];
  }
  return questionWithAnswersData.value;
});

const columns = [
  { key: "question", label: "Question" },
  { key: "answer", label: "Answer" },
];

const visibleRows = computed(() => {
  // Show all rows now that we've removed collapsible functionality
  return rows.value;
});
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
  height: 60px !important;
  min-height: 60px !important;
}

.table-full-width-wrapper tr[aria-expanded="true"],
.table-full-width-wrapper tr.is-expanded,
.table-full-width-wrapper tr.expanded,
.table-full-width-wrapper tr[aria-selected="true"],
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
  padding-top: 0.75rem !important;
  padding-bottom: 0.75rem !important;
}

.table-full-width-wrapper td:first-child,
.table-full-width-wrapper th:first-child {
  width: 60% !important;
}

.table-full-width-wrapper :deep(td:nth-child(2)),
.table-full-width-wrapper :deep(th:nth-child(2)) {
  width: 40%;
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
  display: block;
  width: 100%;
  word-break: break-word;
  padding-top: 0.5em;
}

.answer-link {
  text-decoration: none;
  color: var(--color-cold-purple) !important;
  font-weight: 600 !important;
  font-size: 16px !important;
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
  padding: 1rem 0;
  margin-left: var(--indent);
}

.mobile-card:last-child {
  border-bottom: none;
}

.mobile-card-question {
  margin-bottom: 0.75rem;
}

.mobile-question-text {
  display: block;
  width: 100%;
  word-break: break-word;
  font-size: 14px !important;
  line-height: 26px !important;
}

.mobile-card-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mobile-card-row {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0;
}

.mobile-card-answer {
  color: var(--color-cold-night) !important;
  line-height: 1.6 !important;
}

.mobile-card-answer .answer-link {
  font-size: 16px !important;
}

/* Ensure themes and answers are properly styled on mobile */
@media (max-width: 767px) {
  .answer-link {
    word-break: break-word;
  }
}
</style>
