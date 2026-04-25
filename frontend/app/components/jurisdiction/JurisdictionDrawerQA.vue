<template>
  <div v-if="loading" class="flex flex-col gap-2 py-2">
    <LoadingBar />
    <LoadingBar />
  </div>
  <InlineError
    v-else-if="questionsError || answersError"
    :error="questionsError || answersError"
  />
  <div v-else-if="rows.length > 0" class="divide-y divide-gray-100">
    <div
      v-for="row in rows"
      :key="row.id"
      class="qa-row flex flex-col gap-1 py-3"
      :style="{ paddingLeft: `${row.level * 1.25}em` }"
    >
      <div
        class="text-xs whitespace-pre-line"
        :class="{ 'font-semibold': isBoldQuestion(row.id) }"
      >
        {{ row.question }}
      </div>
      <div v-if="row.answer" class="flex">
        <a
          :href="row.answerLink"
          class="answer-pill max-w-full truncate"
          @click="handleClick($event, row.id)"
        >
          <template v-if="shouldShowDash(row.answer)">—</template>
          <span v-else class="truncate">{{ row.answer }}</span>
        </a>
      </div>
      <span v-else class="text-xs text-gray-400">—</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useQuestions } from "@/composables/useFullTable";
import {
  useAnswersByJurisdictions,
  processAnswerText,
} from "@/composables/useAnswers";
import { useEntityDrawer } from "@/composables/useEntityDrawer";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import InlineError from "@/components/ui/InlineError.vue";

const props = defineProps<{
  jurisdictionCode: string;
}>();

const { openDrawer } = useEntityDrawer();

const BOLD_QUESTIONS = new Set(["03-PA", "07-PA", "08-PA", "09-FoC"]);
const DASH_ANSWERS = new Set([
  "Not applicable",
  "Jurisdiction does not cover this question",
  "No information",
]);

const isBoldQuestion = (id: string) => BOLD_QUESTIONS.has(id);
const shouldShowDash = (answer: string | undefined) =>
  !answer || DASH_ANSWERS.has(answer);

const jurisdictionCodes = computed(() => [
  props.jurisdictionCode.toUpperCase(),
]);

const {
  data: questionsData,
  isLoading: questionsLoading,
  error: questionsError,
} = useQuestions();

const {
  data: answersMap,
  isLoading: answersLoading,
  error: answersError,
} = useAnswersByJurisdictions(jurisdictionCodes);

const loading = computed(() => questionsLoading.value || answersLoading.value);

const rows = computed(() => {
  if (!questionsData.value || !Array.isArray(questionsData.value)) return [];

  const iso3 = props.jurisdictionCode.toUpperCase();
  const sorted = questionsData.value.slice().sort((a, b) => {
    const aId = String(a.id ?? "");
    const bId = String(b.id ?? "");
    return aId.localeCompare(bId);
  });

  return sorted.map((item) => {
    const id = String(item.id ?? "");
    const level = id.match(/\./g)?.length || 0;
    const answerText = answersMap.value?.get(iso3)?.get(id) || "";

    return {
      id,
      question: item.question,
      answer: processAnswerText(answerText),
      answerLink: `/question/${iso3}_${id}`,
      level,
    };
  });
});

function handleClick(event: MouseEvent, questionId: string) {
  if (event.metaKey || event.ctrlKey) return;
  event.preventDefault();
  const iso3 = props.jurisdictionCode.toUpperCase();
  openDrawer(`${iso3}_${questionId}`, "Answers", "/question");
}
</script>

<style scoped>
@reference "tailwindcss";

.qa-row {
  transition: background 0.15s ease;
}

.qa-row:hover {
  background: linear-gradient(
    315deg,
    color-mix(in srgb, var(--color-cold-purple) 2%, white),
    color-mix(in srgb, var(--color-cold-green) 1%, white)
  );
}

.answer-pill {
  @apply rounded-md px-2 py-0.5 text-xs font-medium shadow-sm transition-all duration-150;
  display: inline-block;
  background: var(--gradient-subtle);
  color: var(--color-cold-night);
  cursor: pointer;
}

.answer-pill:hover {
  @apply shadow;
  background: var(--gradient-subtle-emphasis);
  color: var(--color-cold-purple);
}
</style>
