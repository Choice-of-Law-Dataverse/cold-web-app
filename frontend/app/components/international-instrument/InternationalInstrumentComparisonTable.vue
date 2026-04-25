<template>
  <UCard
    id="hcch-answers"
    :ui="{
      body: '!p-0',
      header: 'border-b-0 px-6 py-5',
    }"
  >
    <template #header>
      <h3 class="comparison-title">HCCH Questions &amp; Answers</h3>
    </template>

    <template #default>
      <div class="gradient-top-border" />

      <div class="overflow-hidden px-6 py-5">
        <div class="mb-6">
          <div
            class="flex flex-col items-stretch gap-4 md:flex-row md:items-center"
          >
            <h4 class="comparison-label">Add comparison with</h4>

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
        </div>

        <InlineError v-if="answersError" :error="answersError" />

        <div v-else-if="!hasComparison" class="question-list">
          <div
            v-for="row in rows"
            :id="`hcch-${row.hcchColdId}`"
            :key="row.hcchColdId"
            class="question-row flex flex-col gap-2 py-3.5 md:flex-row md:items-center md:gap-4"
            :style="{ paddingLeft: `calc(1.5rem + ${row.level * 2}em)` }"
          >
            <div
              class="min-w-0 flex-1 text-sm whitespace-pre-line"
              :class="{ 'font-semibold': isBoldQuestion(row.questionColdId) }"
            >
              <span class="inline-block max-w-[68ch]">{{ row.question }}</span>
            </div>

            <div class="flex shrink-0 items-center md:w-[200px] md:justify-end">
              <UTooltip
                v-if="row.instrumentAnswer"
                :text="row.instrumentAnswer"
                :disabled="shouldShowDash(row.instrumentAnswer)"
                :delay-duration="300"
              >
                <a
                  :href="`/hcch-answer/${row.hcchColdId}`"
                  class="answer-button max-w-full truncate"
                  @click="handleHcchClick($event, row.hcchColdId)"
                >
                  <template v-if="shouldShowDash(row.instrumentAnswer)"
                    >—</template
                  >
                  <span v-else class="truncate">{{
                    row.instrumentAnswer
                  }}</span>
                </a>
              </UTooltip>
              <span v-else class="answer-button text-gray-400">—</span>
            </div>
          </div>
        </div>

        <div v-else>
          <div class="mb-6 flex flex-wrap gap-2 md:hidden">
            <UBadge
              color="neutral"
              variant="soft"
              class="text-md"
              :title="instrumentName"
            >
              <div class="inline-flex items-center gap-2">
                <UIcon
                  name="i-material-symbols:gavel-rounded"
                  class="h-4 w-4"
                />
                <span>{{ instrumentBadgeLabel }}</span>
              </div>
            </UBadge>
            <UBadge
              v-for="jurisdiction in comparisonJurisdictions"
              :key="jurisdiction.coldId || jurisdiction.name"
              color="neutral"
              variant="soft"
              class="text-md cursor-pointer hover:bg-gray-200"
              :title="jurisdiction.name"
              @click="removeJurisdiction(jurisdiction.coldId)"
            >
              <div class="inline-flex items-center gap-2">
                <img
                  v-if="jurisdiction.avatar"
                  :src="jurisdiction.avatar"
                  :alt="`${jurisdiction.name} flag`"
                  class="h-3.5 w-5 rounded-sm object-cover"
                />
                <span>{{ jurisdictionLabel(jurisdiction) }}</span>
                <UIcon name="i-heroicons-x-mark-20-solid" class="h-4 w-4" />
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
                class="comparison-header-cell sticky top-0 bg-white py-3 text-center"
                :class="isScrollable ? 'sticky-col-2' : ''"
                :style="isScrollable ? { left: stickyColLeft } : {}"
              >
                <button
                  type="button"
                  class="jurisdiction-action-button"
                  :title="instrumentName"
                  disabled
                >
                  <UIcon
                    name="i-material-symbols:gavel-rounded"
                    class="h-4 w-4 flex-shrink-0"
                  />
                  <span class="min-w-0 truncate">{{
                    instrumentBadgeLabel
                  }}</span>
                </button>
              </div>

              <div
                v-for="jurisdiction in comparisonJurisdictions"
                :key="'h-' + (jurisdiction.coldId || jurisdiction.name)"
                class="comparison-header-cell sticky top-0 bg-white py-3 text-center"
              >
                <button
                  type="button"
                  class="jurisdiction-action-button removable"
                  :title="jurisdiction.name"
                  @click="removeJurisdiction(jurisdiction.coldId)"
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
                    name="i-heroicons-x-mark-20-solid"
                    class="h-4 w-4 flex-shrink-0"
                  />
                </button>
              </div>

              <div
                v-for="row in rows"
                :key="row.hcchColdId"
                class="comparison-row"
              >
                <div
                  :id="`hcch-${row.hcchColdId}`"
                  class="comparison-cell comparison-cell--question text-sm whitespace-pre-line"
                  :class="[
                    { 'font-semibold': isBoldQuestion(row.questionColdId) },
                    { 'sticky-col-1': isScrollable },
                  ]"
                  :style="{ paddingLeft: `${row.level * 2}em` }"
                >
                  {{ row.question }}
                </div>

                <div
                  class="comparison-cell comparison-cell--answer"
                  :class="{ 'sticky-col-2': isScrollable }"
                  :style="isScrollable ? { left: stickyColLeft } : {}"
                >
                  <UTooltip
                    v-if="row.instrumentAnswer"
                    :text="row.instrumentAnswer"
                    :disabled="shouldShowDash(row.instrumentAnswer)"
                    :delay-duration="300"
                  >
                    <a
                      :href="`/hcch-answer/${row.hcchColdId}`"
                      class="answer-button"
                      @click="handleHcchClick($event, row.hcchColdId)"
                    >
                      <template v-if="shouldShowDash(row.instrumentAnswer)">
                        —
                      </template>
                      <span v-else class="line-clamp-2">{{
                        row.instrumentAnswer
                      }}</span>
                    </a>
                  </UTooltip>
                  <span v-else class="text-gray-400">—</span>
                </div>

                <div
                  v-for="jurisdiction in comparisonJurisdictions"
                  :key="jurisdiction.coldId || jurisdiction.name"
                  class="comparison-cell comparison-cell--answer"
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
                      jurisdiction.coldId &&
                      row.jurisdictionAnswers[jurisdiction.coldId]
                    "
                    :text="row.jurisdictionAnswers[jurisdiction.coldId]"
                    :disabled="
                      shouldShowDash(
                        row.jurisdictionAnswers[jurisdiction.coldId],
                      )
                    "
                    :delay-duration="300"
                  >
                    <a
                      :href="
                        getAnswerLink(jurisdiction.coldId, row.questionColdId)
                      "
                      class="answer-button"
                      @click="
                        handleAnswerClick(
                          $event,
                          jurisdiction.coldId,
                          row.questionColdId,
                        )
                      "
                    >
                      <template
                        v-if="
                          shouldShowDash(
                            row.jurisdictionAnswers[jurisdiction.coldId],
                          )
                        "
                      >
                        —
                      </template>
                      <span v-else class="line-clamp-2">{{
                        row.jurisdictionAnswers[jurisdiction.coldId]
                      }}</span>
                    </a>
                  </UTooltip>
                  <span v-else class="text-gray-400">—</span>
                </div>
              </div>
            </div>
          </div>

          <div class="question-list block md:hidden">
            <div
              v-for="row in rows"
              :id="`hcch-mobile-${row.hcchColdId}`"
              :key="row.hcchColdId"
              class="question-row py-3.5"
              :style="{ paddingLeft: `calc(1.5rem + ${row.level * 2}em)` }"
            >
              <div
                class="mb-3 text-sm whitespace-pre-line"
                :class="{ 'font-semibold': isBoldQuestion(row.questionColdId) }"
              >
                {{ row.question }}
              </div>

              <div class="flex flex-wrap gap-4">
                <a
                  v-if="row.instrumentAnswer"
                  :href="`/hcch-answer/${row.hcchColdId}`"
                  class="answer-button !inline-flex max-w-[10rem] items-center gap-2"
                  @click="handleHcchClick($event, row.hcchColdId)"
                >
                  <UIcon
                    name="i-material-symbols:gavel-rounded"
                    class="h-3.5 w-3.5 flex-shrink-0"
                  />
                  <template v-if="shouldShowDash(row.instrumentAnswer)">
                    —
                  </template>
                  <span v-else class="min-w-0 truncate">{{
                    row.instrumentAnswer
                  }}</span>
                </a>
                <span v-else class="text-gray-400">—</span>

                <div
                  v-for="jurisdiction in comparisonJurisdictions"
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
                      jurisdiction.coldId &&
                      row.jurisdictionAnswers[jurisdiction.coldId]
                    "
                    :href="
                      getAnswerLink(jurisdiction.coldId, row.questionColdId)
                    "
                    class="answer-button !inline-flex max-w-[10rem] items-center gap-2"
                    @click="
                      handleAnswerClick(
                        $event,
                        jurisdiction.coldId,
                        row.questionColdId,
                      )
                    "
                  >
                    <img
                      v-if="jurisdiction.avatar"
                      :src="jurisdiction.avatar"
                      :alt="`${jurisdiction.name} flag`"
                      class="h-2 w-3 flex-shrink-0 object-cover"
                    />
                    <template
                      v-if="
                        shouldShowDash(
                          row.jurisdictionAnswers[jurisdiction.coldId],
                        )
                      "
                    >
                      —
                    </template>
                    <span v-else class="min-w-0 truncate">{{
                      row.jurisdictionAnswers[jurisdiction.coldId]
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

interface HcchAnswerRow {
  id: number;
  coldId?: string | null;
  adaptedQuestion?: string | null;
  position?: string | null;
}

const props = defineProps<{
  instrumentName: string;
  instrumentColdId: string;
  hcchAnswers: HcchAnswerRow[];
}>();

const { openDrawer } = useEntityDrawer();
const route = useRoute();

const comparisonJurisdictions = ref<JurisdictionOption[]>([]);
const selectedJurisdiction = ref<JurisdictionOption | undefined>(undefined);

const {
  data: allJurisdictionsData,
  isLoading: jurisdictionsLoading,
  error: jurisdictionsError,
} = useJurisdictions();

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

watch(
  comparisonJurisdictions,
  () => {
    const codes = comparisonJurisdictions.value
      .map((j) => j.coldId)
      .filter((code): code is string => Boolean(code));

    const url = new URL(window.location.href);

    if (codes.length > 0) {
      url.searchParams.delete("compare");
      codes.forEach((code) => url.searchParams.append("compare", code));
    } else {
      url.searchParams.delete("compare");
    }

    url.hash = "#hcch-answers";
    window.history.replaceState({}, "", url.toString());
  },
  { deep: true },
);

const excludedJurisdictionCodes = computed(() => {
  const codes: Array<string | undefined> = [];
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

const hasComparison = computed(() => comparisonJurisdictions.value.length > 0);

const BOLD_QUESTIONS = new Set(["03-PA", "07-PA", "08-PA", "09-FoC"]);
const isBoldQuestion = (questionColdId: string) =>
  BOLD_QUESTIONS.has(questionColdId);

const DASH_ANSWERS = new Set([
  "Not applicable",
  "Jurisdiction does not cover this question",
  "No information",
]);
const shouldShowDash = (answer: string | undefined | null) =>
  !answer || DASH_ANSWERS.has(answer);

const jurisdictionCodes = computed(() =>
  comparisonJurisdictions.value
    .map((j) => j.coldId)
    .filter((code): code is string => Boolean(code)),
);

const {
  data: answersMap,
  isLoading: answersLoading,
  error: answersError,
} = useAnswersByJurisdictions(jurisdictionCodes);

const totalColumns = computed(() => 1 + comparisonJurisdictions.value.length);
const useShortLabels = computed(() => totalColumns.value >= 4);
const isScrollable = computed(() => totalColumns.value >= 5);

const gridTemplateColumns = computed(() => {
  const count = totalColumns.value;
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
  return `${questionCol} ${answerCols}`;
});

const stickyColLeft = computed(() => {
  const count = totalColumns.value;
  if (count >= 7) return "220px";
  if (count >= 5) return "280px";
  return "0";
});

const instrumentBadgeLabel = computed(() => {
  const match = props.instrumentName.match(/\(([^)]+)\)\s*$/);
  if (match?.[1]) return match[1];
  return useShortLabels.value
    ? props.instrumentColdId || props.instrumentName
    : props.instrumentName;
});

const jurisdictionLabel = (j: JurisdictionOption) =>
  useShortLabels.value && j.coldId ? j.coldId : j.name;

const getAnswerLink = (coldId: string, questionId: string) =>
  `/question/${coldId}_${questionId}`;

const loadedJurisdictions = computed(() => {
  if (!answersMap.value) return new Set<string>();
  return new Set(answersMap.value.keys());
});

const hasAnswersForJurisdiction = (coldId?: string) => {
  if (!coldId) return false;
  return loadedJurisdictions.value.has(coldId.toUpperCase());
};

const stripHcchPrefix = (coldId: string) => coldId.replace(/^HCCH-/i, "");

const rows = computed(() => {
  return props.hcchAnswers
    .filter((a) => a.adaptedQuestion || a.position)
    .slice()
    .sort((a, b) =>
      (a.coldId ?? "").localeCompare(b.coldId ?? "", undefined, {
        numeric: true,
      }),
    )
    .map((answer) => {
      const hcchColdId = answer.coldId ?? "";
      const questionColdId = stripHcchPrefix(hcchColdId);
      const level = (questionColdId.match(/\./g) ?? []).length;

      const jurisdictionAnswers: Record<string, string> = {};
      for (const jurisdiction of comparisonJurisdictions.value) {
        const iso3 = jurisdiction.coldId?.toUpperCase();
        if (iso3) {
          const answerText =
            answersMap.value?.get(iso3)?.get(questionColdId) || "";
          jurisdictionAnswers[iso3] = processAnswerText(answerText);
        }
      }

      return {
        hcchColdId,
        questionColdId,
        question: answer.adaptedQuestion || "Question",
        instrumentAnswer: answer.position || "",
        jurisdictionAnswers,
        level,
      };
    });
});

function handleAnswerClick(
  event: MouseEvent,
  coldId: string,
  questionId: string,
) {
  if (event.metaKey || event.ctrlKey) return;
  event.preventDefault();
  openDrawer(`${coldId}_${questionId}`, "Answers", "/question");
}

function handleHcchClick(event: MouseEvent, hcchColdId: string) {
  if (event.metaKey || event.ctrlKey) return;
  event.preventDefault();
  openDrawer(hcchColdId, "HCCH Answers", "/hcch-answer");
}
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
</style>
