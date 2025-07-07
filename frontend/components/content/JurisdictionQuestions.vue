<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <UCard class="cold-ucard">
          <div>
            <h2 class="mb-10">Questions and Answers for Switzerland</h2>
            <div class="result-value-small table-full-width-wrapper">
              <UTable :rows="people" />
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </main>
</template>

<script setup>
const people = [
  {
    question: 'Is there a codification on choice of law?',
    answer: 'Yes',
  },
  {
    question:
      'Do the courts have the authority to refer to the HCCH Principles as persuasive authority?',
    answer: 'Yes',
  },
  {
    question:
      'Is the principle of party autonomy in respect of choice of law in international commercial contracts widely accepted in this jurisdiction?',
    answer: 'No',
  },
  {
    question:
      'More specifically, are the parties to an international commercial contract allowed to choose the law applicable to their contract?',
    answer: 'No',
  },
]
</script>

<style scoped>
.result-value-small,
.result-value-small :deep(td),
.result-value-small :deep(th),
.result-value-small :deep(tr),
.result-value-small :deep(span),
.result-value-small :deep(div) {
  color: var(--color-cold-night) !important;
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
}

.table-full-width-wrapper :deep(tr) {
  height: 72px;
  min-height: 72px;
}

.table-full-width-wrapper :deep(thead) {
  display: none;
}

.table-full-width-wrapper :deep(th),
.table-full-width-wrapper :deep(td) {
  border-bottom: 1px solid var(--color-cold-gray) !important;
  border-top: 1px solid var(--color-cold-gray) !important;
}
</style>
