<template>
  <div class="comparison-row">
    <div
      :id="`question-${row.id}`"
      class="comparison-cell comparison-cell--question text-sm whitespace-pre-line"
      :class="[
        { 'font-semibold': isBoldQuestion(row.id) },
        { 'sticky-col-1': isScrollable },
      ]"
      :style="{ paddingLeft: `${row.level * 2}em` }"
    >
      {{ row.question }}
    </div>

    <div
      v-for="(jurisdiction, jIndex) in jurisdictions"
      :key="jurisdiction.coldId || jurisdiction.name"
      class="comparison-cell comparison-cell--answer"
      :class="{ 'sticky-col-2': jIndex === 0 && isScrollable }"
      :style="jIndex === 0 && isScrollable ? { left: stickyColLeft } : {}"
    >
      <div
        v-if="answersLoading && !hasAnswersForJurisdiction(jurisdiction.coldId)"
      >
        <USkeleton class="h-4 w-16" />
      </div>
      <UTooltip
        v-else-if="jurisdiction.coldId && row.answers?.[jurisdiction.coldId]"
        :text="row.answers[jurisdiction.coldId]"
        :disabled="shouldShowDash(row.answers[jurisdiction.coldId])"
        :delay-duration="300"
      >
        <a
          :href="getAnswerLink(jurisdiction.coldId, row.id)"
          class="answer-button"
          @click="handleAnswerClick($event, jurisdiction.coldId, row.id)"
        >
          <template v-if="shouldShowDash(row.answers[jurisdiction.coldId])">
            —
          </template>
          <span v-else class="line-clamp-2">{{
            row.answers[jurisdiction.coldId]
          }}</span>
        </a>
      </UTooltip>
      <span v-else class="text-gray-400">—</span>
    </div>

    <div
      class="comparison-cell comparison-cell--match"
      :class="isScrollable ? 'sticky-col-match' : ''"
    >
      <USkeleton
        v-if="!allJurisdictionsHaveAnswersLoaded"
        class="h-4 w-4 rounded-full"
      />
      <UIcon
        v-else-if="row.matchStatus === 'match'"
        name="i-material-symbols:check-circle-rounded"
        class="match-indicator match-indicator--match"
        :title="`All ${jurisdictions.length} jurisdictions agree`"
      />
      <UIcon
        v-else-if="row.matchStatus === 'mismatch'"
        name="i-material-symbols:remove-rounded"
        class="match-indicator match-indicator--mismatch"
        title="Answers differ"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { inject } from "vue";
import { ComparisonStateKey } from "./comparisonState";
import type { Row } from "./comparisonState";

defineProps<{
  row: Row;
}>();

const state = inject(ComparisonStateKey);
if (!state) throw new Error("Comparison state not provided");

const {
  jurisdictions,
  answersLoading,
  isScrollable,
  stickyColLeft,
  allJurisdictionsHaveAnswersLoaded,
  hasAnswersForJurisdiction,
  shouldShowDash,
  handleAnswerClick,
  getAnswerLink,
  isBoldQuestion,
} = state;
</script>
