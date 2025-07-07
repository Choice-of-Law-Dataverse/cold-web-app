<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <UCard class="cold-ucard">
          <div>
            <h2 class="mt-2 mb-8">
              Questions and Answers for Switzerland
              <InfoTooltip text="Questions" class="info-tooltip-small" />
            </h2>

            <div class="table-full-width-wrapper">
              <UTable v-model:expand="expand" :rows="people" :columns="columns">
                <template #theme-data="{ row }">
                  <span :class="row.theme.class">{{ row.theme.value }}</span>
                </template>

                <template #expand="{ row }">
                  <div class="p-4">
                    <pre>{{ row }}</pre>
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
import InfoTooltip from '@/components/ui/InfoTooltip.vue'

const people = [
  {
    question: 'Is there a codification on choice of law?',
    theme: { value: 'Codification', class: 'label-theme' },
    answer: 'Yes',
  },
  {
    question:
      'Do the courts have the authority to refer to the HCCH Principles as persuasive authority?',
    theme: {
      value: 'Codification, HCCH Principles',
      class: 'label-theme',
    },
    answer: 'Yes',
  },
  {
    question:
      'Is the principle of party autonomy in respect of choice of law in international commercial contracts widely accepted in this jurisdiction?',
    theme: {
      value: 'Party autonomy, Freedom of choice',
      class: 'label-theme',
    },
    answer: 'No',
  },
  {
    question:
      'More specifically, are the parties to an international commercial contract allowed to choose the law applicable to their contract?',
    theme: {
      value: 'Party autonomy, Freedom of choice',
      class: 'label-theme',
    },
    answer: 'No',
  },
]

const columns = [
  { key: 'question', label: 'Question' },
  { key: 'theme', label: 'Theme' },
  { key: 'answer', label: 'Answer' },
]

const expand = ref({
  openedRows: [people[0]],
  row: {},
})
</script>

<style scoped>
.result-value-small,
.result-value-small :deep(td),
.result-value-small :deep(th),
.result-value-small :deep(tr),
.result-value-small :deep(span),
.result-value-small :deep(div) {
  color: var(--color-cold-night) !important;
  line-height: 26px !important;
}

.table-full-width-wrapper {
  /* Remove padding from the UCard for this table only */
  margin-left: calc(-1 * var(--card-padding, 1.5rem));
  margin-right: calc(-1 * var(--card-padding, 1.5rem));
  width: calc(100% + 2 * var(--card-padding, 1.5rem));
  margin-bottom: -1.55rem !important;
}
.table-full-width-wrapper :deep(table) {
  width: 100% !important;
  table-layout: auto;
  table-layout: fixed;
}

.table-full-width-wrapper :deep(td),
.table-full-width-wrapper :deep(th) {
  white-space: normal !important;
  word-break: break-word !important;
  overflow-wrap: break-word !important;
}

.table-full-width-wrapper :deep(tr) {
  height: 80px;
  min-height: 80px;
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

.table-full-width-wrapper :deep(td:first-child),
.table-full-width-wrapper :deep(th:first-child) {
  width: 36px !important;
  min-width: 32px !important;
  max-width: 40px !important;
  padding-left: 1rem !important;
}
.table-full-width-wrapper :deep(td:nth-child(2)),
.table-full-width-wrapper :deep(th:nth-child(2)) {
  width: 50%;
}
.table-full-width-wrapper :deep(td:nth-child(3)),
.table-full-width-wrapper :deep(th:nth-child(3)) {
  width: 40%;
  text-align: right !important;
}
.table-full-width-wrapper :deep(td:nth-child(4)),
.table-full-width-wrapper :deep(th:nth-child(4)) {
  width: 10%;
  text-align: right !important;
  padding-right: 2em !important;
}

.info-tooltip-small :deep(.icon-span) {
  font-size: 0.75em !important;
}
</style>
