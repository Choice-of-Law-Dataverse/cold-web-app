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

          <div v-if="matchStats" class="comparison-match-stats-wrapper">
            <div class="comparison-match-stats">
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
              <span
                class="comparison-match-stats__divider"
                aria-hidden="true"
              />
              <button
                type="button"
                class="comparison-caveats__trigger"
                :aria-expanded="showCaveats"
                @click="showCaveats = !showCaveats"
              >
                <UIcon
                  name="i-material-symbols:info-outline"
                  class="comparison-caveats__trigger-icon"
                />
                About these numbers
              </button>
            </div>
          </div>
          <div
            v-if="matchStats && showCaveats"
            class="comparison-caveats__body"
          >
            <p>A few caveats should be expressed at the outset:</p>
            <ul>
              <li>
                Simplification may be necessary to concentrate on a limited
                number of key options that legislators, courts, or further
                authorities may have when implementing, interpreting, or
                applying a specific rule regarding an issue addressed in the
                <NuxtLink to="/learn/methodology#questionnaire">
                  Questionnaire </NuxtLink
                >.
              </li>
              <li>
                Similarly, it is difficult to adequately compare the individual
                instruments or jurisdictions in view of the different legal
                methods used in various parts of the world, and the varying
                degree of sophistication. A certain degree of asymmetry of
                information must be taken into consideration; while some
                specialists were able to rely on sophisticated codifications of
                PIL rules, or numerous court decisions and academic writings,
                such privileges were not available to specialists of some of the
                countries where party choice of law is limited, or rarely
                practiced.
              </li>
              <li>
                Finally, CoLD deals with legal cultures that address choice of
                law problems in different ways, as prominently illustrated by
                the dichotomy between common-law and civil-law jurisdictions.
                For example, various jurisdictions based in the common-law
                tradition have not enacted PIL codifications addressing party
                choice of law, whereas many civil law-based jurisdictions have
                enacted, or are in the process of enacting, such codifications.
                These differences have a direct impact on the methods used by
                courts and practitioners to apply, and interpret, rules dealing
                with choice of law, the results of which are sometimes difficult
                to compare.
              </li>
              <li>
                At times, a sophisticated user may find that the Comparison tool
                is an attempt to compare apples with oranges. This phenomenon is
                not atypical in comparative law. We strongly recommend
                consulting the additional information linked to the answers (by
                clicking on it).
              </li>
            </ul>
            <h4 class="comparison-caveats__heading">
              Availability of information
            </h4>
            <p>
              Many specialists in private international law, with a focus on
              their respective jurisdictions, have contributed to the data
              collection. Their names are indicated in the country report.
              Nevertheless, certain jurisdictions may contain more data points
              than others. This might be related to:
            </p>
            <ul>
              <li>availability of information about choice of law rules;</li>
              <li>
                importance of the jurisdiction from an economic, social, or
                cultural perspective;
              </li>
              <li>availability of specialists.</li>
            </ul>
          </div>
        </div>

        <InlineError v-if="answersError" :error="answersError" />

        <div v-else-if="!hasComparison" class="question-list">
          <template v-for="item in groupedRows" :key="item.key">
            <div v-if="item.type === 'theme-header'" class="theme-header">
              <span class="theme-header__name">{{ item.theme }}</span>
            </div>
            <div
              v-else
              :id="`hcch-${item.row.hcchColdId}`"
              class="question-row flex flex-col gap-2 py-3.5 md:flex-row md:items-center md:gap-4"
              :style="{ paddingLeft: `calc(1.5rem + ${item.row.level * 2}em)` }"
            >
              <div
                class="min-w-0 flex-1 text-sm whitespace-pre-line"
                :class="{
                  'font-semibold': isBoldQuestion(item.row.questionColdId),
                }"
              >
                <span class="inline-block max-w-[68ch]">{{
                  item.row.question
                }}</span>
              </div>

              <div
                class="flex shrink-0 items-center md:w-[200px] md:justify-end"
              >
                <UTooltip
                  v-if="item.row.instrumentAnswer"
                  :text="item.row.instrumentAnswer"
                  :disabled="shouldShowDash(item.row.instrumentAnswer)"
                  :delay-duration="300"
                >
                  <a
                    :href="`/hcch-answer/${item.row.hcchColdId}`"
                    class="answer-button max-w-full truncate"
                    @click="handleHcchClick($event, item.row.hcchColdId)"
                  >
                    <template v-if="shouldShowDash(item.row.instrumentAnswer)">
                      —
                    </template>
                    <span v-else class="truncate">{{
                      item.row.instrumentAnswer
                    }}</span>
                  </a>
                </UTooltip>
                <span v-else class="answer-button text-gray-400">—</span>
              </div>
            </div>
          </template>
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
                class="comparison-header-cell comparison-header-cell--match sticky top-0 bg-white py-3"
                :class="isScrollable ? 'sticky-col-match' : ''"
                aria-hidden="true"
              />

              <template v-for="item in groupedRows" :key="item.key">
                <div
                  v-if="item.type === 'theme-header'"
                  class="comparison-theme-header"
                >
                  <span class="theme-header__name">{{ item.theme }}</span>
                  <span v-if="item.stats" class="theme-header__stats">
                    {{ item.stats.percentage }}% match
                    <span class="theme-header__stats-detail">
                      ({{ item.stats.matching }} of {{ item.stats.total }})
                    </span>
                  </span>
                </div>
                <div v-else class="comparison-row">
                  <div
                    :id="`hcch-${item.row.hcchColdId}`"
                    class="comparison-cell comparison-cell--question text-sm whitespace-pre-line"
                    :class="[
                      {
                        'font-semibold': isBoldQuestion(
                          item.row.questionColdId,
                        ),
                      },
                      { 'sticky-col-1': isScrollable },
                    ]"
                    :style="{ paddingLeft: `${item.row.level * 2}em` }"
                  >
                    {{ item.row.question }}
                  </div>

                  <div
                    class="comparison-cell comparison-cell--answer"
                    :class="{ 'sticky-col-2': isScrollable }"
                    :style="isScrollable ? { left: stickyColLeft } : {}"
                  >
                    <UTooltip
                      v-if="item.row.instrumentAnswer"
                      :text="item.row.instrumentAnswer"
                      :disabled="shouldShowDash(item.row.instrumentAnswer)"
                      :delay-duration="300"
                    >
                      <a
                        :href="`/hcch-answer/${item.row.hcchColdId}`"
                        class="answer-button"
                        @click="handleHcchClick($event, item.row.hcchColdId)"
                      >
                        <template
                          v-if="shouldShowDash(item.row.instrumentAnswer)"
                        >
                          —
                        </template>
                        <span v-else class="line-clamp-2">{{
                          item.row.instrumentAnswer
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
                        item.row.jurisdictionAnswers[jurisdiction.coldId]
                      "
                      :text="item.row.jurisdictionAnswers[jurisdiction.coldId]"
                      :disabled="
                        shouldShowDash(
                          item.row.jurisdictionAnswers[jurisdiction.coldId],
                        )
                      "
                      :delay-duration="300"
                    >
                      <a
                        :href="
                          getAnswerLink(
                            jurisdiction.coldId,
                            item.row.questionColdId,
                          )
                        "
                        class="answer-button"
                        @click="
                          handleAnswerClick(
                            $event,
                            jurisdiction.coldId,
                            item.row.questionColdId,
                          )
                        "
                      >
                        <template
                          v-if="
                            shouldShowDash(
                              item.row.jurisdictionAnswers[jurisdiction.coldId],
                            )
                          "
                        >
                          —
                        </template>
                        <span v-else class="line-clamp-2">{{
                          item.row.jurisdictionAnswers[jurisdiction.coldId]
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
                      v-else-if="item.row.matchStatus === 'match'"
                      name="i-material-symbols:check-circle-rounded"
                      class="match-indicator match-indicator--match"
                      :title="`Instrument and ${comparisonJurisdictions.length} jurisdiction${comparisonJurisdictions.length === 1 ? '' : 's'} agree`"
                    />
                    <UIcon
                      v-else-if="item.row.matchStatus === 'mismatch'"
                      name="i-material-symbols:remove-rounded"
                      class="match-indicator match-indicator--mismatch"
                      title="Answers differ"
                    />
                  </div>
                </div>
              </template>
            </div>
          </div>

          <div class="question-list block md:hidden">
            <template v-for="item in groupedRows" :key="item.key">
              <div v-if="item.type === 'theme-header'" class="theme-header">
                <span class="theme-header__name">{{ item.theme }}</span>
                <span v-if="item.stats" class="theme-header__stats">
                  {{ item.stats.percentage }}% match
                  <span class="theme-header__stats-detail">
                    ({{ item.stats.matching }} of {{ item.stats.total }})
                  </span>
                </span>
              </div>
              <div
                v-else
                :id="`hcch-mobile-${item.row.hcchColdId}`"
                class="question-row py-3.5"
                :style="{
                  paddingLeft: `calc(1.5rem + ${item.row.level * 2}em)`,
                }"
              >
                <div
                  class="mb-3 flex items-start gap-2 text-sm whitespace-pre-line"
                  :class="{
                    'font-semibold': isBoldQuestion(item.row.questionColdId),
                  }"
                >
                  <span class="min-w-0 flex-1">{{ item.row.question }}</span>
                  <UIcon
                    v-if="
                      allJurisdictionsHaveAnswersLoaded &&
                      item.row.matchStatus === 'match'
                    "
                    name="i-material-symbols:check-circle-rounded"
                    class="match-indicator match-indicator--match mt-0.5 shrink-0"
                  />
                  <UIcon
                    v-else-if="
                      allJurisdictionsHaveAnswersLoaded &&
                      item.row.matchStatus === 'mismatch'
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
                  <a
                    v-if="item.row.instrumentAnswer"
                    :href="`/hcch-answer/${item.row.hcchColdId}`"
                    class="answer-button !inline-flex max-w-[10rem] items-center gap-2"
                    @click="handleHcchClick($event, item.row.hcchColdId)"
                  >
                    <UIcon
                      name="i-material-symbols:gavel-rounded"
                      class="h-3.5 w-3.5 flex-shrink-0"
                    />
                    <template v-if="shouldShowDash(item.row.instrumentAnswer)">
                      —
                    </template>
                    <span v-else class="min-w-0 truncate">{{
                      item.row.instrumentAnswer
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
                        item.row.jurisdictionAnswers[jurisdiction.coldId]
                      "
                      :href="
                        getAnswerLink(
                          jurisdiction.coldId,
                          item.row.questionColdId,
                        )
                      "
                      class="answer-button !inline-flex max-w-[10rem] items-center gap-2"
                      @click="
                        handleAnswerClick(
                          $event,
                          jurisdiction.coldId,
                          item.row.questionColdId,
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
                            item.row.jurisdictionAnswers[jurisdiction.coldId],
                          )
                        "
                      >
                        —
                      </template>
                      <span v-else class="min-w-0 truncate">{{
                        item.row.jurisdictionAnswers[jurisdiction.coldId]
                      }}</span>
                    </a>
                    <span v-else class="text-gray-400">—</span>
                  </div>
                </div>
              </div>
            </template>
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
const showCaveats = ref(false);

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
  "No provision",
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

const MATCH_COL_WIDTH = 44;

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
  return `${questionCol} ${answerCols} ${MATCH_COL_WIDTH}px`;
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

const allJurisdictionsHaveAnswersLoaded = computed(() =>
  jurisdictionCodes.value.every((code) => hasAnswersForJurisdiction(code)),
);

const stripHcchPrefix = (coldId: string) => coldId.replace(/^HCCH-/i, "");

type MatchStatus = "match" | "mismatch" | "na";

const normalizeAnswerForMatch = (value: string) =>
  !value || DASH_ANSWERS.has(value) ? "—" : value;

const getMatchStatus = (values: string[]): MatchStatus => {
  if (values.length < 2) return "na";
  const normalized = values.map(normalizeAnswerForMatch);
  return new Set(normalized).size === 1 ? "match" : "mismatch";
};

interface Row {
  hcchColdId: string;
  questionColdId: string;
  question: string;
  instrumentAnswer: string;
  jurisdictionAnswers: Record<string, string>;
  matchStatus: MatchStatus;
  level: number;
  theme: string;
}

type MatchStats = { matching: number; total: number; percentage: number };

type GroupedRow =
  | {
      type: "theme-header";
      theme: string;
      stats: MatchStats | null;
      key: string;
    }
  | { type: "question"; row: Row; key: string };

function aggregateMatchStats(items: Row[]): MatchStats | null {
  let total = 0;
  let matching = 0;
  for (const row of items) {
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
}

const THEME_NAME_BY_CODE: Record<string, string> = {
  P: "Codification",
  PA: "Party Autonomy",
  FoC: "Freedom of Choice",
  TC: "Tacit Choice",
  AoC: "Absence of Choice",
  MR: "Overriding Mandatory Rules",
  PP: "Public Policy",
  Arb: "Arbitration",
};

const THEME_ORDER_BY_NAME = new Map(
  Object.values(THEME_NAME_BY_CODE).map((name, idx) => [name, idx]),
);

function themeCodeFromId(id: string): string | null {
  const match = id.match(/-([A-Za-z]+)$/);
  return match?.[1] ?? null;
}

const rows = computed<Row[]>(() => {
  const filtered = props.hcchAnswers.filter(
    (a) => a.adaptedQuestion || a.position,
  );

  const sorted = filtered.slice().sort((a, b) =>
    (a.coldId ?? "").localeCompare(b.coldId ?? "", undefined, {
      numeric: true,
    }),
  );

  return sorted.flatMap<Row>((answer) => {
    const hcchColdId = answer.coldId ?? "";
    const questionColdId = stripHcchPrefix(hcchColdId);
    const code = themeCodeFromId(questionColdId);
    const themeName = code ? THEME_NAME_BY_CODE[code] : undefined;
    if (!code || !themeName) return [];
    const level = (questionColdId.match(/\./g) ?? []).length;

    const instrumentAnswer = answer.position ?? "";
    const jurisdictionAnswers: Record<string, string> = {};
    for (const jurisdiction of comparisonJurisdictions.value) {
      const iso3 = jurisdiction.coldId?.toUpperCase();
      if (iso3) {
        const answerText =
          answersMap.value?.get(iso3)?.get(questionColdId) || "";
        jurisdictionAnswers[iso3] = processAnswerText(answerText);
      }
    }

    const matchValues = hasComparison.value
      ? [instrumentAnswer, ...Object.values(jurisdictionAnswers)]
      : [];

    return [
      {
        hcchColdId,
        questionColdId,
        question: answer.adaptedQuestion || "Question",
        instrumentAnswer,
        jurisdictionAnswers,
        matchStatus: getMatchStatus(matchValues),
        level,
        theme: themeName,
      },
    ];
  });
});

const groupedRows = computed<GroupedRow[]>(() => {
  const groups = new Map<string, Row[]>();
  for (const row of rows.value) {
    const bucket = groups.get(row.theme) ?? [];
    bucket.push(row);
    groups.set(row.theme, bucket);
  }

  const ordered = [...groups.entries()].sort(([a], [b]) => {
    const ai = THEME_ORDER_BY_NAME.get(a) ?? Number.MAX_SAFE_INTEGER;
    const bi = THEME_ORDER_BY_NAME.get(b) ?? Number.MAX_SAFE_INTEGER;
    return ai - bi;
  });

  const showStats =
    hasComparison.value && allJurisdictionsHaveAnswersLoaded.value;
  const out: GroupedRow[] = [];
  for (const [theme, themeRows] of ordered) {
    out.push({
      type: "theme-header",
      theme,
      stats: showStats ? aggregateMatchStats(themeRows) : null,
      key: `theme:${theme}`,
    });
    for (const row of themeRows) {
      out.push({ type: "question", row, key: `q:${row.hcchColdId}` });
    }
  }
  return out;
});

const matchStats = computed(() => {
  if (!hasComparison.value) return null;
  if (!allJurisdictionsHaveAnswersLoaded.value) return null;
  return aggregateMatchStats(rows.value);
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

.theme-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.5rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-cold-night-alpha);
}

.theme-header:first-child {
  padding-top: 0.25rem;
}

.comparison-theme-header {
  grid-column: 1 / -1;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 0.5rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-cold-night-alpha);
  border-bottom: 1px solid var(--color-gray-100, #f3f4f6);
}

.comparison-theme-header:first-of-type {
  padding-top: 0.25rem;
}

.theme-header__name {
  min-width: 0;
}

.theme-header__stats {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0;
  text-transform: none;
  color: var(--color-cold-night-alpha);
  white-space: nowrap;
}

.theme-header__stats-detail {
  font-size: 0.6875rem;
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

.comparison-header-cell--match {
  padding-inline: 0;
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

.sticky-col-1 {
  position: sticky;
  left: 0;
  z-index: 30;
  background: white;
}

.comparison-row:hover .sticky-col-1,
.comparison-row:hover .sticky-col-2,
.comparison-row:hover .sticky-col-match {
  background: inherit;
}

.sticky-col-2 {
  position: sticky;
  z-index: 20;
  background: white;
}

.sticky-col-match {
  position: sticky;
  right: 0;
  z-index: 35;
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
  color: var(--color-cold-night-alpha);
}

.comparison-match-stats-wrapper {
  margin-top: 0.875rem;
  display: flex;
  justify-content: flex-end;
}

.comparison-match-stats {
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

.comparison-match-stats__divider {
  width: 1px;
  align-self: stretch;
  margin: 0 0.25rem;
  background: color-mix(in srgb, var(--color-cold-night) 12%, transparent);
}

.comparison-caveats__trigger {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-cold-night-alpha);
  cursor: pointer;
  background: transparent;
  border: 0;
  padding: 0;
}

.comparison-caveats__trigger:hover {
  color: var(--color-cold-night);
}

.comparison-caveats__trigger-icon {
  width: 0.875rem;
  height: 0.875rem;
}

.comparison-caveats__body {
  margin-top: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: 6px;
  background: var(--gradient-subtle);
  font-size: 0.8125rem;
  line-height: 1.55;
  color: var(--color-cold-night);
}

.comparison-caveats__body p,
.comparison-caveats__body ul {
  margin: 0 0 0.75rem;
}

.comparison-caveats__body ul {
  padding-left: 1.25rem;
  list-style: disc;
}

.comparison-caveats__body li + li {
  margin-top: 0.5rem;
}

.comparison-caveats__body :deep(a) {
  color: var(--color-cold-purple);
  text-decoration: underline;
}

.comparison-caveats__heading {
  margin: 1rem 0 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-cold-night);
}
</style>
