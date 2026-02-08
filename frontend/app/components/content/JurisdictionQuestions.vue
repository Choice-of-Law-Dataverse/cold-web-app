<template>
  <UCard
    id="questions-and-answers"
    :ui="{
      body: '!p-0',
      header: 'border-b-0 px-6 py-5',
    }"
  >
    <template #header>
      <div class="flex justify-between">
        <h3 class="comparison-title">Comparison</h3>
        <span class="flex flex-wrap gap-2">
          <NuxtLink to="/learn/methodology" class="answer-button gap-2">
            <UIcon
              :name="'i-material-symbols:school-outline'"
              class="inline-block text-[1.2em]"
            />
            Methodology
          </NuxtLink>
          <NuxtLink to="/learn/glossary" class="answer-button gap-2">
            <UIcon
              :name="'i-material-symbols:dictionary-outline'"
              class="inline-block text-[1.2em]"
            />
            Glossary
          </NuxtLink>
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
            <h4 class="text-left text-base md:whitespace-nowrap">
              Add comparison with
            </h4>

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

        <div v-else-if="isSingleJurisdiction" class="divide-y divide-gray-100">
          <div
            v-for="row in rows"
            :id="`question-${row.id}`"
            :key="row.id"
            class="question-row hover-row--emphasis flex flex-col gap-2 px-2 py-4 md:flex-row md:items-center md:gap-4"
            :style="{ paddingLeft: `${row.level * 2}em` }"
          >
            <div
              class="min-w-0 flex-1 text-sm whitespace-pre-line"
              :class="{ 'font-semibold': isBoldQuestion(row.id) }"
            >
              <span class="inline-block max-w-[72ch]">{{ row.question }}</span>
            </div>

            <div class="flex shrink-0 items-center md:w-[200px] md:justify-end">
              <NuxtLink
                v-if="row.answer"
                :to="row.answerLink"
                class="answer-button max-w-full truncate"
              >
                <template v-if="shouldShowDash(row.answer)">—</template>
                <span v-else class="truncate">{{ row.answer }}</span>
              </NuxtLink>
              <span v-else class="answer-button text-gray-400">—</span>
            </div>
          </div>
        </div>

        <div v-else>
          <div class="mb-6 flex flex-wrap gap-2 md:hidden">
            <UBadge
              v-for="(jurisdiction, index) in jurisdictions"
              :key="jurisdiction.alpha3Code || jurisdiction.Name"
              color="neutral"
              variant="soft"
              :class="
                index > 0
                  ? 'text-md cursor-pointer hover:bg-gray-200'
                  : 'text-md'
              "
              :title="jurisdiction.Name"
              @click="
                index > 0 ? removeJurisdiction(jurisdiction.alpha3Code) : null
              "
            >
              <div class="inline-flex items-center gap-2">
                <img
                  v-if="jurisdiction.avatar"
                  :src="jurisdiction.avatar"
                  :alt="`${jurisdiction.Name} flag`"
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
                class="comparison-header-cell sticky top-0 bg-white py-3 font-semibold"
                :class="isScrollable ? 'sticky-col-1' : ''"
              >
                Question
              </div>
              <div
                v-for="(jurisdiction, index) in jurisdictions"
                :key="'h-' + (jurisdiction.alpha3Code || jurisdiction.Name)"
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
                  :title="jurisdiction.Name"
                  :disabled="index === 0"
                  @click="
                    index > 0
                      ? removeJurisdiction(jurisdiction.alpha3Code)
                      : null
                  "
                >
                  <img
                    v-if="jurisdiction.avatar"
                    :src="jurisdiction.avatar"
                    :alt="`${jurisdiction.Name} flag`"
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

              <template v-for="row in rows" :key="row.id">
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
                  :key="jurisdiction.alpha3Code || jurisdiction.Name"
                  class="comparison-cell comparison-cell--answer"
                  :class="{ 'sticky-col-2': jIndex === 0 && isScrollable }"
                  :style="
                    jIndex === 0 && isScrollable ? { left: stickyColLeft } : {}
                  "
                >
                  <div
                    v-if="
                      answersLoading &&
                      !hasAnswersForJurisdiction(jurisdiction.alpha3Code)
                    "
                  >
                    <USkeleton class="h-4 w-16" />
                  </div>
                  <NuxtLink
                    v-else-if="
                      jurisdiction.alpha3Code &&
                      row.answers?.[jurisdiction.alpha3Code]
                    "
                    :to="getAnswerLink(jurisdiction.alpha3Code, row.id)"
                    class="answer-button"
                  >
                    <template
                      v-if="
                        shouldShowDash(row.answers[jurisdiction.alpha3Code])
                      "
                    >
                      —
                    </template>
                    <span v-else class="line-clamp-2">{{
                      row.answers[jurisdiction.alpha3Code]
                    }}</span>
                  </NuxtLink>
                  <span v-else class="text-gray-400">—</span>
                </div>
              </template>
            </div>
          </div>

          <div class="block divide-y divide-gray-100 md:hidden">
            <div
              v-for="row in rows"
              :id="`question-${row.id}`"
              :key="row.id"
              class="question-row px-2 py-4"
              :style="{ paddingLeft: `${row.level * 2}em` }"
            >
              <div
                class="mb-3 text-sm whitespace-pre-line"
                :class="{ 'font-semibold': isBoldQuestion(row.id) }"
              >
                {{ row.question }}
              </div>

              <div class="flex flex-wrap gap-4">
                <div
                  v-for="jurisdiction in jurisdictions"
                  :key="jurisdiction.alpha3Code || jurisdiction.Name"
                  class="flex items-center gap-2"
                >
                  <div
                    v-if="
                      answersLoading &&
                      !hasAnswersForJurisdiction(jurisdiction.alpha3Code)
                    "
                    class="flex items-center gap-2"
                  >
                    <img
                      v-if="jurisdiction.avatar"
                      :src="jurisdiction.avatar"
                      :alt="`${jurisdiction.Name} flag`"
                      class="h-2 w-3 object-cover"
                    />
                    <USkeleton class="h-4 w-16" />
                  </div>
                  <NuxtLink
                    v-else-if="
                      jurisdiction.alpha3Code &&
                      row.answers?.[jurisdiction.alpha3Code]
                    "
                    :to="getAnswerLink(jurisdiction.alpha3Code, row.id)"
                    class="answer-button !inline-flex max-w-[10rem] items-center gap-2"
                  >
                    <img
                      v-if="jurisdiction.avatar"
                      :src="jurisdiction.avatar"
                      :alt="`${jurisdiction.Name} flag`"
                      class="h-2 w-3 flex-shrink-0 object-cover"
                    />
                    <template
                      v-if="
                        shouldShowDash(row.answers[jurisdiction.alpha3Code])
                      "
                    >
                      —
                    </template>
                    <span v-else class="min-w-0 truncate">{{
                      row.answers[jurisdiction.alpha3Code]
                    }}</span>
                  </NuxtLink>
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
import JurisdictionSelectMenu from "@/components/jurisdiction-comparison/JurisdictionSelectMenu.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import InlineError from "@/components/ui/InlineError.vue";
import type { JurisdictionOption } from "@/types/analyzer";

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
          (j) => j.alpha3Code?.toUpperCase() === code.toString().toUpperCase(),
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
      .map((j) => j.alpha3Code)
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
  const codes = [props.primaryJurisdiction.alpha3Code];
  comparisonJurisdictions.value.forEach((j) => {
    if (j.alpha3Code) codes.push(j.alpha3Code);
  });
  return codes.filter(Boolean);
});

const handleAddJurisdiction = (
  jurisdiction: JurisdictionOption | undefined,
) => {
  if (!jurisdiction?.alpha3Code) return;

  const alreadySelected = comparisonJurisdictions.value.some(
    (j) =>
      j.alpha3Code?.toUpperCase() === jurisdiction.alpha3Code?.toUpperCase(),
  );

  if (!alreadySelected) {
    comparisonJurisdictions.value.push(jurisdiction);
    selectedJurisdiction.value = undefined;
  }
};

const removeJurisdiction = (alpha3Code?: string) => {
  if (!alpha3Code) return;
  const codeToRemove = alpha3Code.toUpperCase();
  comparisonJurisdictions.value = comparisonJurisdictions.value.filter(
    (j) => j.alpha3Code?.toUpperCase() !== codeToRemove,
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
    .map((j) => j.alpha3Code)
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
  return `${questionCol} ${answerCols}`;
});

const stickyColLeft = computed(() => {
  const count = jurisdictions.value.length;
  if (count >= 7) return "220px";
  if (count >= 5) return "280px";
  return "0";
});

const jurisdictionLabel = (j: JurisdictionOption) =>
  useShortLabels.value && j.alpha3Code ? j.alpha3Code : j.Name;

const getAnswerLink = (alpha3Code: string, questionId: string) => {
  return `/question/${alpha3Code}_${questionId}`;
};

const loadedJurisdictions = computed(() => {
  if (!answersMap.value) return new Set<string>();
  return new Set(answersMap.value.keys());
});

const hasAnswersForJurisdiction = (alpha3Code?: string) => {
  if (!alpha3Code) return false;
  const upperCode = alpha3Code.toUpperCase();
  return loadedJurisdictions.value.has(upperCode);
};

const rows = computed(() => {
  if (!questionsData.value || !Array.isArray(questionsData.value)) {
    return [];
  }

  const sorted = questionsData.value.slice().sort((a, b) => {
    const aId = a.ID ?? "";
    const bId = b.ID ?? "";
    return aId.localeCompare(bId);
  });

  return sorted.map((item) => {
    const id = item.ID ?? "";
    const level = typeof id === "string" ? id.match(/\./g)?.length || 0 : 0;

    // Backward compatible format for single jurisdiction
    if (isSingleJurisdiction.value) {
      const iso3 = jurisdictionCodes.value[0]?.toUpperCase();
      const answerText = iso3 ? answersMap.value?.get(iso3)?.get(id) || "" : "";
      const answerDisplay = processAnswerText(answerText);

      return {
        id,
        question: item.Question,
        answer: answerDisplay,
        answerLink: `/question/${iso3}_${id}`,
        level,
      };
    }

    // Answers map for multiple jurisdictions
    const answers: Record<string, string> = {};
    for (const jurisdiction of jurisdictions.value) {
      const iso3 = jurisdiction.alpha3Code?.toUpperCase();
      if (iso3) {
        const answerText = answersMap.value?.get(iso3)?.get(id) || "";
        answers[iso3] = processAnswerText(answerText);
      }
    }

    return {
      id,
      question: item.Question,
      answers,
      level,
    };
  });
});
</script>

<style scoped>
@reference "tailwindcss";

.question-row {
  margin: 0 -1rem;
  padding-left: 1rem !important;
  padding-right: 1rem !important;
}

.comparison-grid {
  display: grid;
  gap: 0;
}

.comparison-header-cell {
  padding-inline: 0.25rem;
  border-bottom: 2px solid
    color-mix(in srgb, var(--color-cold-purple) 10%, transparent);
  box-shadow: 0 2px 4px 0 rgb(0 0 0 / 0.05);
  z-index: 5;
}

.comparison-cell {
  padding: 0.75rem 0.25rem;
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
  @apply rounded-lg px-2 py-1 text-sm font-medium shadow-sm transition-all duration-150;
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
