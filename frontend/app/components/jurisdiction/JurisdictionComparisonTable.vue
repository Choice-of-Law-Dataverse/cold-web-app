<template>
  <UCard
    id="questions-and-answers"
    :ui="{
      body: '!p-0',
      header: 'border-b-0 px-6 py-5',
    }"
  >
    <template #header>
      <div class="flex items-center justify-between">
        <h3 class="comparison-title">Comparison</h3>
        <span class="flex flex-wrap gap-1.5">
          <UButton
            to="/learn/methodology"
            color="primary"
            variant="ghost"
            size="xs"
            leading-icon="i-material-symbols:school-outline"
            trailing-icon="i-material-symbols:arrow-forward"
          >
            Methodology
          </UButton>
          <UButton
            to="/learn/glossary"
            color="primary"
            variant="ghost"
            size="xs"
            leading-icon="i-material-symbols:dictionary-outline"
            trailing-icon="i-material-symbols:arrow-forward"
          >
            Glossary
          </UButton>
        </span>
      </div>
    </template>

    <template #default>
      <!-- Gradient divider between header and content -->
      <div class="gradient-top-border" />

      <div class="overflow-hidden px-6 py-5">
        <div v-if="!isSingleJurisdiction || allJurisdictionsData" class="mb-6">
          <div
            class="flex flex-col items-stretch gap-4 md:flex-row md:items-center"
          >
            <h4 class="comparison-label">Add comparison with</h4>

            <!-- Loading state -->
            <div v-if="jurisdictionsLoading" class="flex items-center gap-2">
              <LoadingBar />
            </div>

            <InlineError
              v-else-if="jurisdictionsError"
              :error="jurisdictionsError"
            />

            <div
              v-else
              class="flex flex-1 flex-col gap-4 md:flex-row md:items-center"
            >
              <JurisdictionSelectMenu
                v-model="selectedJurisdiction"
                :jurisdictions="allJurisdictionsData || []"
                :excluded-codes="excludedJurisdictionCodes"
                placeholder="Jurisdiction"
                @jurisdiction-selected="handleAddJurisdiction"
              />
            </div>
          </div>

          <div v-if="matchStats" class="comparison-match-stats">
            <UIcon
              name="i-material-symbols:check-circle-rounded"
              class="comparison-match-stats__icon"
            />
            <span class="comparison-match-stats__value">
              {{ matchStats.percentage }}%
            </span>
            <span class="comparison-match-stats__label">
              matching answers
              <span class="comparison-match-stats__detail">
                ({{ matchStats.matching }} of {{ matchStats.total }}
                {{ matchStats.total === 1 ? "question" : "questions" }})
              </span>
            </span>
          </div>
        </div>

        <div
          v-if="isSingleJurisdiction && (loading || answersLoading)"
          class="flex flex-col space-y-3 py-8"
        >
          <LoadingBar />
          <LoadingBar />
          <LoadingBar />
        </div>

        <InlineError
          v-else-if="questionsError || answersError"
          :error="questionsError || answersError"
        />

        <div v-else-if="isSingleJurisdiction" class="question-list">
          <div
            v-for="row in rows"
            :id="`question-${row.id}`"
            :key="row.id"
            class="question-row flex flex-col gap-2 py-3.5 md:flex-row md:items-center md:gap-4"
            :style="{ paddingLeft: `calc(1.5rem + ${row.level * 2}em)` }"
          >
            <div
              class="min-w-0 flex-1 text-sm whitespace-pre-line"
              :class="{ 'font-semibold': isBoldQuestion(row.id) }"
            >
              <span class="inline-block max-w-[68ch]">{{ row.question }}</span>
            </div>

            <div class="flex shrink-0 items-center md:w-[200px] md:justify-end">
              <UTooltip
                v-if="row.answer"
                :text="row.answer"
                :disabled="shouldShowDash(row.answer)"
                :delay-duration="300"
              >
                <a
                  :href="row.answerLink"
                  class="answer-button max-w-full truncate"
                  @click="
                    handleAnswerClick($event, jurisdictionCodes[0]!, row.id)
                  "
                >
                  <template v-if="shouldShowDash(row.answer)">—</template>
                  <span v-else class="truncate">{{ row.answer }}</span>
                </a>
              </UTooltip>
              <span v-else class="answer-button text-gray-400">—</span>
            </div>
          </div>
        </div>

        <div v-else>
          <div class="mb-6 flex flex-wrap gap-2 md:hidden">
            <UBadge
              v-for="(jurisdiction, index) in jurisdictions"
              :key="jurisdiction.coldId || jurisdiction.name"
              color="neutral"
              variant="soft"
              :class="
                index > 0
                  ? 'text-md cursor-pointer hover:bg-gray-200'
                  : 'text-md'
              "
              :title="jurisdiction.name"
              @click="
                index > 0 ? removeJurisdiction(jurisdiction.coldId) : null
              "
            >
              <div class="inline-flex items-center gap-2">
                <img
                  v-if="jurisdiction.avatar"
                  :src="jurisdiction.avatar"
                  :alt="`${jurisdiction.name} flag`"
                  class="h-3.5 w-5 rounded-sm object-cover"
                />
                <span>{{ jurisdictionLabel(jurisdiction) }}</span>
                <UIcon
                  v-if="index > 0"
                  name="i-heroicons-x-mark-20-solid"
                  class="h-4 w-4"
                />
              </div>
            </UBadge>
          </div>

          <div
            class="hidden md:block"
            :class="{ 'overflow-x-auto': isScrollable }"
          >
            <div class="comparison-grid" :style="{ gridTemplateColumns }">
              <div
                class="comparison-header-cell sticky top-0 bg-white py-3"
                :class="isScrollable ? 'sticky-col-1' : ''"
              >
                <span class="comparison-header-label">Question</span>
              </div>
              <div
                v-for="(jurisdiction, index) in jurisdictions"
                :key="'h-' + (jurisdiction.coldId || jurisdiction.name)"
                class="comparison-header-cell sticky top-0 bg-white py-3 text-center"
                :class="index === 0 && isScrollable ? 'sticky-col-2' : ''"
                :style="
                  index === 0 && isScrollable ? { left: stickyColLeft } : {}
                "
              >
                <button
                  type="button"
                  class="jurisdiction-action-button"
                  :class="{ removable: index > 0 }"
                  :title="jurisdiction.name"
                  :disabled="index === 0"
                  @click="
                    index > 0 ? removeJurisdiction(jurisdiction.coldId) : null
                  "
                >
                  <img
                    v-if="jurisdiction.avatar"
                    :src="jurisdiction.avatar"
                    :alt="`${jurisdiction.name} flag`"
                    class="h-3.5 w-5 flex-shrink-0 rounded-sm object-cover"
                  />
                  <span class="min-w-0 truncate">{{
                    jurisdictionLabel(jurisdiction)
                  }}</span>
                  <UIcon
                    v-if="index > 0"
                    name="i-heroicons-x-mark-20-solid"
                    class="h-4 w-4 flex-shrink-0"
                  />
                </button>
              </div>
              <div
                class="comparison-header-cell comparison-header-cell--match sticky top-0 bg-white py-3"
                :class="isScrollable ? 'sticky-col-match' : ''"
                aria-hidden="true"
              />

              <div v-for="row in rows" :key="row.id" class="comparison-row">
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
                  :style="
                    jIndex === 0 && isScrollable ? { left: stickyColLeft } : {}
                  "
                >
                  <div
                    v-if="
                      answersLoading &&
                      !hasAnswersForJurisdiction(jurisdiction.coldId)
                    "
                  >
                    <USkeleton class="h-4 w-16" />
                  </div>
                  <UTooltip
                    v-else-if="
                      jurisdiction.coldId && row.answers?.[jurisdiction.coldId]
                    "
                    :text="row.answers[jurisdiction.coldId]"
                    :disabled="shouldShowDash(row.answers[jurisdiction.coldId])"
                    :delay-duration="300"
                  >
                    <a
                      :href="getAnswerLink(jurisdiction.coldId, row.id)"
                      class="answer-button"
                      @click="
                        handleAnswerClick($event, jurisdiction.coldId, row.id)
                      "
                    >
                      <template
                        v-if="shouldShowDash(row.answers[jurisdiction.coldId])"
                      >
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
            </div>
          </div>

          <div class="question-list block md:hidden">
            <div
              v-for="row in rows"
              :id="`question-${row.id}`"
              :key="row.id"
              class="question-row py-3.5"
              :style="{ paddingLeft: `calc(1.5rem + ${row.level * 2}em)` }"
            >
              <div
                class="mb-3 flex items-start gap-2 text-sm whitespace-pre-line"
                :class="{ 'font-semibold': isBoldQuestion(row.id) }"
              >
                <span class="min-w-0 flex-1">{{ row.question }}</span>
                <UIcon
                  v-if="
                    allJurisdictionsHaveAnswersLoaded &&
                    row.matchStatus === 'match'
                  "
                  name="i-material-symbols:check-circle-rounded"
                  class="match-indicator match-indicator--match mt-0.5 shrink-0"
                />
                <UIcon
                  v-else-if="
                    allJurisdictionsHaveAnswersLoaded &&
                    row.matchStatus === 'mismatch'
                  "
                  name="i-material-symbols:remove-rounded"
                  class="match-indicator match-indicator--mismatch mt-0.5 shrink-0"
                />
                <span
                  v-else
                  class="match-indicator match-indicator--spacer shrink-0"
                  aria-hidden="true"
                />
              </div>

              <div class="flex flex-wrap gap-4">
                <div
                  v-for="jurisdiction in jurisdictions"
                  :key="jurisdiction.coldId || jurisdiction.name"
                  class="flex items-center gap-2"
                >
                  <div
                    v-if="
                      answersLoading &&
                      !hasAnswersForJurisdiction(jurisdiction.coldId)
                    "
                    class="flex items-center gap-2"
                  >
                    <img
                      v-if="jurisdiction.avatar"
                      :src="jurisdiction.avatar"
                      :alt="`${jurisdiction.name} flag`"
                      class="h-2 w-3 object-cover"
                    />
                    <USkeleton class="h-4 w-16" />
                  </div>
                  <a
                    v-else-if="
                      jurisdiction.coldId && row.answers?.[jurisdiction.coldId]
                    "
                    :href="getAnswerLink(jurisdiction.coldId, row.id)"
                    class="answer-button !inline-flex max-w-[10rem] items-center gap-2"
                    @click="
                      handleAnswerClick($event, jurisdiction.coldId, row.id)
                    "
                  >
                    <img
                      v-if="jurisdiction.avatar"
                      :src="jurisdiction.avatar"
                      :alt="`${jurisdiction.name} flag`"
                      class="h-2 w-3 flex-shrink-0 object-cover"
                    />
                    <template
                      v-if="shouldShowDash(row.answers[jurisdiction.coldId])"
                    >
                      —
                    </template>
                    <span v-else class="min-w-0 truncate">{{
                      row.answers[jurisdiction.coldId]
                    }}</span>
                  </a>
                  <span v-else class="text-gray-400">—</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </UCard>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useQuestions } from "@/composables/useFullTable";
import {
  useAnswersByJurisdictions,
  processAnswerText,
} from "~/composables/useAnswers";
import { useJurisdictions } from "@/composables/useJurisdictions";
import JurisdictionSelectMenu from "@/components/jurisdiction/JurisdictionSelectMenu.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import InlineError from "@/components/ui/InlineError.vue";
import { useEntityDrawer } from "@/composables/useEntityDrawer";
import type { JurisdictionOption } from "@/types/analyzer";

const { openDrawer } = useEntityDrawer();

function handleAnswerClick(
  event: MouseEvent,
  coldId: string,
  questionId: string,
) {
  if (event.metaKey || event.ctrlKey) return;
  event.preventDefault();
  openDrawer(`${coldId}_${questionId}`, "Answers", "/question");
}

// Props - now only needs the primary jurisdiction
const props = defineProps<{
  primaryJurisdiction: JurisdictionOption;
}>();

const route = useRoute();

// Track comparison jurisdictions
const comparisonJurisdictions = ref<JurisdictionOption[]>([]);

// Track selected value for the selector (to reset after selection)
const selectedJurisdiction = ref<JurisdictionOption | undefined>(undefined);

// Get all available jurisdictions
const {
  data: allJurisdictionsData,
  isLoading: jurisdictionsLoading,
  error: jurisdictionsError,
} = useJurisdictions();

// Initialize comparison jurisdictions from URL query params on mount
onMounted(() => {
  const compareParam = route.query.compare;
  if (compareParam && allJurisdictionsData.value) {
    const compareCodes = Array.isArray(compareParam)
      ? compareParam
      : [compareParam];
    const jurisdictionsToAdd = compareCodes
      .filter((code) => code != null)
      .map((code) =>
        allJurisdictionsData.value?.find(
          (j) => j.coldId?.toUpperCase() === code.toString().toUpperCase(),
        ),
      )
      .filter((j): j is NonNullable<typeof j> => Boolean(j));

    comparisonJurisdictions.value = jurisdictionsToAdd;
  }
});

// Use history API instead of router to avoid scroll-to-top
watch(
  comparisonJurisdictions,
  async (newJurisdictions) => {
    const codes = newJurisdictions
      .map((j) => j.coldId)
      .filter((code): code is string => Boolean(code));

    const url = new URL(window.location.href);

    if (codes.length > 0) {
      url.searchParams.delete("compare");
      codes.forEach((code) => url.searchParams.append("compare", code));
    } else {
      url.searchParams.delete("compare");
    }

    url.hash = "#questions-and-answers";
    window.history.replaceState({}, "", url.toString());
  },
  { deep: true },
);

// Primary + selected comparison jurisdictions
const excludedJurisdictionCodes = computed(() => {
  const codes = [props.primaryJurisdiction.coldId];
  comparisonJurisdictions.value.forEach((j) => {
    if (j.coldId) codes.push(j.coldId);
  });
  return codes.filter(Boolean);
});

const handleAddJurisdiction = (
  jurisdiction: JurisdictionOption | undefined,
) => {
  if (!jurisdiction?.coldId) return;

  const alreadySelected = comparisonJurisdictions.value.some(
    (j) => j.coldId?.toUpperCase() === jurisdiction.coldId?.toUpperCase(),
  );

  if (!alreadySelected) {
    comparisonJurisdictions.value.push(jurisdiction);
    selectedJurisdiction.value = undefined;
  }
};

const removeJurisdiction = (coldId?: string) => {
  if (!coldId) return;
  const codeToRemove = coldId.toUpperCase();
  comparisonJurisdictions.value = comparisonJurisdictions.value.filter(
    (j) => j.coldId?.toUpperCase() !== codeToRemove,
  );
};

const jurisdictions = computed(() => {
  return [props.primaryJurisdiction, ...comparisonJurisdictions.value];
});

// Hard-coded questions to render in bold
const BOLD_QUESTIONS = new Set(["03-PA", "07-PA", "08-PA", "09-FoC"]);

const isBoldQuestion = (questionId: string) => {
  return BOLD_QUESTIONS.has(questionId);
};

// Answers to display as a dash
const DASH_ANSWERS = new Set([
  "Not applicable",
  "Jurisdiction does not cover this question",
  "No information",
]);

const shouldShowDash = (answer: string | undefined) => {
  return !answer || DASH_ANSWERS.has(answer);
};

const jurisdictionCodes = computed(() =>
  jurisdictions.value
    .map((j) => j.coldId)
    .filter((code): code is string => Boolean(code)),
);

// Fetch questions and answers separately
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

const loading = computed(() => questionsLoading.value);

const isSingleJurisdiction = computed(() => jurisdictions.value.length === 1);

const useShortLabels = computed(() => jurisdictions.value.length >= 4);

const isScrollable = computed(() => jurisdictions.value.length >= 5);

const MATCH_COL_WIDTH = 44;

const gridTemplateColumns = computed(() => {
  const count = jurisdictions.value.length;
  let questionCol: string;
  let answerCol: string;
  if (count >= 7) {
    questionCol = "220px";
    answerCol = "140px";
  } else if (count >= 5) {
    questionCol = "280px";
    answerCol = "160px";
  } else {
    questionCol = "minmax(0, 2fr)";
    answerCol = "minmax(0, 1fr)";
  }
  const answerCols = Array(count).fill(answerCol).join(" ");
  return `${questionCol} ${answerCols} ${MATCH_COL_WIDTH}px`;
});

const stickyColLeft = computed(() => {
  const count = jurisdictions.value.length;
  if (count >= 7) return "220px";
  if (count >= 5) return "280px";
  return "0";
});

const jurisdictionLabel = (j: JurisdictionOption) =>
  useShortLabels.value && j.coldId ? j.coldId : j.name;

const getAnswerLink = (coldId: string, questionId: string) => {
  return `/question/${coldId}_${questionId}`;
};

const loadedJurisdictions = computed(() => {
  if (!answersMap.value) return new Set<string>();
  return new Set(answersMap.value.keys());
});

const hasAnswersForJurisdiction = (coldId?: string) => {
  if (!coldId) return false;
  const upperCode = coldId.toUpperCase();
  return loadedJurisdictions.value.has(upperCode);
};

const allJurisdictionsHaveAnswersLoaded = computed(() =>
  jurisdictionCodes.value.every((code) => hasAnswersForJurisdiction(code)),
);

type MatchStatus = "match" | "mismatch" | "na";

const normalizeAnswerForMatch = (value: string) =>
  !value || DASH_ANSWERS.has(value) ? "—" : value;

const getMatchStatus = (answers: Record<string, string>): MatchStatus => {
  const values = Object.values(answers);
  if (values.length < 2) return "na";
  const normalized = values.map(normalizeAnswerForMatch);
  return new Set(normalized).size === 1 ? "match" : "mismatch";
};

const rows = computed(() => {
  if (!questionsData.value || !Array.isArray(questionsData.value)) {
    return [];
  }

  const sorted = questionsData.value.slice().sort((a, b) => {
    const aId = String(a.id ?? "");
    const bId = String(b.id ?? "");
    return aId.localeCompare(bId);
  });

  return sorted.map((item) => {
    const id = String(item.id ?? "");
    const level = typeof id === "string" ? id.match(/\./g)?.length || 0 : 0;

    // Backward compatible format for single jurisdiction
    if (isSingleJurisdiction.value) {
      const iso3 = jurisdictionCodes.value[0]?.toUpperCase();
      const answerText = iso3 ? answersMap.value?.get(iso3)?.get(id) || "" : "";
      const answerDisplay = processAnswerText(answerText);

      return {
        id,
        question: item.question,
        answer: answerDisplay,
        answerLink: `/question/${iso3}_${id}`,
        answers: undefined,
        matchStatus: "na" as MatchStatus,
        level,
      };
    }

    // Answers map for multiple jurisdictions
    const answers: Record<string, string> = {};
    for (const jurisdiction of jurisdictions.value) {
      const iso3 = jurisdiction.coldId?.toUpperCase();
      if (iso3) {
        const answerText = answersMap.value?.get(iso3)?.get(id) || "";
        answers[iso3] = processAnswerText(answerText);
      }
    }

    return {
      id,
      question: item.question,
      answer: undefined,
      answerLink: undefined,
      answers,
      matchStatus: getMatchStatus(answers),
      level,
    };
  });
});

const matchStats = computed(() => {
  if (isSingleJurisdiction.value) return null;
  if (!allJurisdictionsHaveAnswersLoaded.value) return null;
  let total = 0;
  let matching = 0;
  for (const row of rows.value) {
    if (row.matchStatus === "na") continue;
    total++;
    if (row.matchStatus === "match") matching++;
  }
  if (total === 0) return null;
  return {
    total,
    matching,
    percentage: Math.round((matching / total) * 100),
  };
});
</script>

<style scoped>
@reference "tailwindcss";

.comparison-label {
  font-size: 0.8125rem;
  font-weight: 500;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: var(--color-cold-night-alpha);
  text-align: left;
  white-space: nowrap;
}

.question-list {
  margin: 0 -1.5rem;
}

.question-row {
  padding-right: 1.5rem;
  border-radius: 0;
  transition: background 0.15s ease;
}

.question-row:hover {
  background: var(--gradient-subtle-hover);
}

.comparison-grid {
  display: grid;
  gap: 0;
}

.comparison-header-cell {
  padding-inline: 0.5rem;
  border-bottom: 1.5px solid
    color-mix(in srgb, var(--color-cold-purple) 12%, transparent);
  z-index: 5;
}

.comparison-header-label {
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-cold-night-alpha);
}

.comparison-row {
  display: grid;
  grid-column: 1 / -1;
  grid-template-columns: subgrid;
  border-radius: 2px;
  transition: background 0.15s ease;
}

.comparison-row:hover {
  background: var(--gradient-subtle-hover);
}

.comparison-cell {
  padding: 0.75rem 0.5rem;
  border-bottom: 1px solid var(--color-gray-100, #f3f4f6);
  min-width: 0;
  overflow: hidden;
}

.comparison-cell--question {
  align-content: center;
}

.comparison-cell--answer {
  text-align: center;
  align-content: center;
}

.sticky-col-1 {
  position: sticky;
  left: 0;
  z-index: 30;
  background: white;
}

.comparison-row:hover .sticky-col-1,
.comparison-row:hover .sticky-col-2 {
  background: inherit;
}

.sticky-col-2 {
  position: sticky;
  z-index: 20;
  background: white;
}

.jurisdiction-action-button {
  @apply inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-all;
  color: var(--color-cold-night);
  background: white;
  border: 1.5px solid
    color-mix(in srgb, var(--color-cold-night) 25%, transparent);
}

.jurisdiction-action-button:disabled {
  cursor: default;
}

.jurisdiction-action-button.removable {
  cursor: pointer;
}

.jurisdiction-action-button.removable:hover {
  background: var(--color-cold-night);
  color: white;
  border-color: var(--color-cold-night);
}

.answer-button {
  @apply rounded-md px-2.5 py-1 text-sm font-medium shadow-sm transition-all duration-150;
  display: inline-block;
  min-width: 3.5rem;
  max-width: 100%;
  overflow: hidden;
  background: var(--gradient-subtle);
  color: var(--color-cold-night);
  cursor: pointer;
  text-align: center;
  vertical-align: middle;
}

.answer-button:hover {
  @apply shadow;
  background: var(--gradient-subtle-emphasis);
  color: var(--color-cold-purple);
}

.comparison-header-cell--match {
  padding-inline: 0;
}

.comparison-cell--match {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 0;
}

.match-indicator {
  width: 1.125rem;
  height: 1.125rem;
}

.match-indicator--match {
  color: var(--color-emerald-500, #10b981);
}

.match-indicator--mismatch {
  color: var(--color-amber-500, #f59e0b);
}

.match-indicator--spacer {
  display: inline-block;
}

.sticky-col-match {
  position: sticky;
  right: 0;
  z-index: 35;
  background: white;
}

.comparison-row:hover .sticky-col-match {
  background: inherit;
}

.comparison-match-stats {
  margin-top: 0.875rem;
  display: inline-flex;
  align-items: baseline;
  gap: 0.5rem;
  padding: 0.5rem 0.875rem;
  border-radius: 6px;
  background: var(--gradient-subtle);
}

.comparison-match-stats__icon {
  position: relative;
  top: 2px;
  width: 1rem;
  height: 1rem;
  color: var(--color-emerald-500, #10b981);
}

.comparison-match-stats__value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-cold-night);
}

.comparison-match-stats__label {
  font-size: 0.8125rem;
  color: var(--color-cold-night-alpha);
}

.comparison-match-stats__detail {
  font-size: 0.75rem;
}
</style>
