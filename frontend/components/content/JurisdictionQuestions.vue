<template>
  <UCard id="questions-and-answers" class="cold-ucard overflow-visible">
    <div class="overflow-hidden">
      <h2 class="mb-8 mt-2">Questions and Answers {{ jurisdictionName }}</h2>

      <div v-if="!isSingleJurisdiction || allJurisdictionsData" class="mb-6">
        <div
          class="flex flex-col items-stretch gap-4 md:flex-row md:items-center"
        >
          <h3 class="text-left text-base md:whitespace-nowrap">
            Add comparison with
          </h3>

          <div
            v-if="!jurisdictionsLoading"
            class="flex flex-col gap-4 md:flex-row md:items-center"
          >
            <JurisdictionSelectMenu
              v-model="selectedJurisdiction"
              :countries="allJurisdictionsData || []"
              :excluded-codes="excludedJurisdictionCodes"
              placeholder="Jurisdiction"
              @country-selected="handleAddJurisdiction"
            />
          </div>

          <!-- Loading state -->
          <div v-else class="flex items-center gap-2">
            <span class="text-sm text-gray-600">Loading jurisdictions...</span>
          </div>
        </div>
      </div>

      <div
        v-if="loading || answersLoading"
        class="flex flex-col space-y-3 py-8"
      >
        <LoadingBar />
        <LoadingBar />
        <LoadingBar />
      </div>

      <div v-else-if="isSingleJurisdiction" class="divide-y divide-cold-gray">
        <div
          v-for="row in rows"
          :id="`question-${row.id}`"
          :key="row.id"
          class="flex flex-col gap-2 py-3 md:flex-row md:items-center md:gap-4"
          :style="{ paddingLeft: `${row.level * 2}em` }"
        >
          <div
            class="whitespace-pre-line text-sm md:w-[60%]"
            :class="{ 'font-bold': isBoldQuestion(row.id) }"
          >
            {{ row.question }}
          </div>

          <div class="md:w-[40%] md:text-right">
            <NuxtLink
              v-if="row.answer"
              :to="row.answerLink"
              class="font-semibold text-cold-purple hover:underline"
            >
              {{ row.answer }}
            </NuxtLink>
            <span v-else>{{ row.answer }}</span>
          </div>
        </div>
      </div>

      <div v-else>
        <div class="mb-6 flex flex-wrap gap-2 md:hidden">
          <UBadge
            v-for="(jurisdiction, index) in jurisdictions"
            :key="jurisdiction.alpha3Code || jurisdiction.Name"
            color="gray"
            variant="soft"
            :class="
              index > 0 ? 'text-md cursor-pointer hover:bg-gray-200' : 'text-md'
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
              >
              <span>{{ jurisdiction.Name }}</span>
              <UIcon
                v-if="index > 0"
                name="i-heroicons-x-mark-20-solid"
                class="h-4 w-4"
              />
            </div>
          </UBadge>
        </div>

        <div class="hidden md:block">
          <div class="divide-y divide-cold-gray">
            <div
              class="flex gap-4 border-b-2 border-cold-gray py-3 font-semibold"
            >
              <div class="w-[40%]">Question</div>
              <div
                v-for="(jurisdiction, index) in jurisdictions"
                :key="jurisdiction.alpha3Code || jurisdiction.Name"
                class="min-w-0 flex-1 text-center"
              >
                <UBadge
                  color="gray"
                  variant="soft"
                  class="text-md inline-flex max-w-full"
                  :class="index > 0 ? 'cursor-pointer hover:bg-gray-200' : ''"
                  :title="jurisdiction.Name"
                  @click="
                    index > 0
                      ? removeJurisdiction(jurisdiction.alpha3Code)
                      : null
                  "
                >
                  <div
                    class="inline-flex min-w-0 max-w-full items-center gap-1.5"
                  >
                    <img
                      v-if="jurisdiction.avatar"
                      :src="jurisdiction.avatar"
                      :alt="`${jurisdiction.Name} flag`"
                      class="h-3.5 w-5 flex-shrink-0 rounded-sm object-cover"
                    >
                    <span class="min-w-0 truncate">{{
                      jurisdiction.Name
                    }}</span>
                    <UIcon
                      v-if="index > 0"
                      name="i-heroicons-x-mark-20-solid"
                      class="h-4 w-4 flex-shrink-0"
                    />
                  </div>
                </UBadge>
              </div>
            </div>
            <div
              v-for="row in rows"
              :id="`question-${row.id}`"
              :key="row.id"
              class="flex gap-4 py-3"
            >
              <div
                class="w-[40%] whitespace-pre-line text-sm"
                :class="{ 'font-bold': isBoldQuestion(row.id) }"
                :style="{ paddingLeft: `${row.level * 2}em` }"
              >
                {{ row.question }}
              </div>

              <div
                v-for="jurisdiction in jurisdictions"
                :key="jurisdiction.alpha3Code || jurisdiction.Name"
                class="flex-1 text-center"
              >
                <NuxtLink
                  v-if="
                    jurisdiction.alpha3Code &&
                    row.answers?.[jurisdiction.alpha3Code]
                  "
                  :to="getAnswerLink(jurisdiction.alpha3Code, row.id)"
                  class="font-semibold text-cold-purple hover:underline"
                >
                  {{ row.answers[jurisdiction.alpha3Code] }}
                </NuxtLink>
                <span v-else>-</span>
              </div>
            </div>
          </div>
        </div>

        <div class="block divide-y divide-cold-gray md:hidden">
          <div
            v-for="row in rows"
            :id="`question-${row.id}`"
            :key="row.id"
            class="py-3"
            :style="{ paddingLeft: `${row.level * 2}em` }"
          >
            <div
              class="mb-3 whitespace-pre-line text-sm"
              :class="{ 'font-bold': isBoldQuestion(row.id) }"
            >
              {{ row.question }}
            </div>

            <div class="flex flex-wrap gap-4">
              <div
                v-for="jurisdiction in jurisdictions"
                :key="jurisdiction.alpha3Code || jurisdiction.Name"
                class="flex items-center gap-2"
              >
                <NuxtLink
                  v-if="
                    jurisdiction.alpha3Code &&
                    row.answers?.[jurisdiction.alpha3Code]
                  "
                  :to="getAnswerLink(jurisdiction.alpha3Code, row.id)"
                  class="flex items-center gap-2 font-semibold text-cold-purple hover:underline"
                >
                  <img
                    v-if="jurisdiction.avatar"
                    :src="jurisdiction.avatar"
                    :alt="`${jurisdiction.Name} flag`"
                    class="h-2 w-3 object-cover"
                  >
                  {{ row.answers[jurisdiction.alpha3Code] }}
                </NuxtLink>
                <span v-else>-</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from "vue";
import { useRoute } from "vue-router";
import {
  useQuestionsWithAnswers,
  processAnswerText,
} from "@/composables/useQuestionsWithAnswers";
import { useJurisdictions } from "@/composables/useJurisdictions";
import JurisdictionSelectMenu from "@/components/jurisdiction-comparison/JurisdictionSelectMenu.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";

// Props - now only needs the primary jurisdiction
const props = defineProps<{
  primaryJurisdiction: {
    Name: string;
    alpha3Code?: string;
    avatar?: string;
    [key: string]: unknown;
  };
}>();

const route = useRoute();

// Track comparison jurisdictions
const comparisonJurisdictions = ref<
  Array<{
    Name: string;
    alpha3Code?: string;
    avatar?: string;
    [key: string]: unknown;
  }>
>([]);

// Track selected value for the selector (to reset after selection)
const selectedJurisdiction = ref(null);

// Get all available jurisdictions
const { data: allJurisdictionsData, isLoading: jurisdictionsLoading } =
  useJurisdictions();

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
  jurisdiction: typeof props.primaryJurisdiction,
) => {
  if (!jurisdiction?.alpha3Code) return;

  const alreadySelected = comparisonJurisdictions.value.some(
    (j) =>
      j.alpha3Code?.toUpperCase() === jurisdiction.alpha3Code?.toUpperCase(),
  );

  if (!alreadySelected) {
    comparisonJurisdictions.value.push(jurisdiction);
    selectedJurisdiction.value = null;
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

const jurisdictionCodes = computed(() =>
  jurisdictions.value
    .map((j) => j.alpha3Code)
    .filter((code): code is string => Boolean(code)),
);

const { questionsData, answersMap, loading, answersLoading } =
  useQuestionsWithAnswers(jurisdictionCodes);

const isSingleJurisdiction = computed(() => jurisdictions.value.length === 1);

const jurisdictionName = computed(() => {
  if (isSingleJurisdiction.value) {
    return props.primaryJurisdiction?.Name
      ? `for ${props.primaryJurisdiction.Name}`
      : "";
  }
  return `- Comparison`;
});

const getAnswerLink = (alpha3Code: string, questionId: string) => {
  return `/question/${alpha3Code}_${questionId}`;
};

const rows = computed(() => {
  if (!questionsData.value || !Array.isArray(questionsData.value)) {
    return [];
  }

  const sorted = (
    questionsData.value as Array<{
      "CoLD ID"?: string;
      ID?: string;
      Question: string;
      Themes?: string;
      [key: string]: unknown;
    }>
  )
    .slice()
    .sort((a, b) => {
      const aId = (a["CoLD ID"] ?? a.ID ?? "") as string;
      const bId = (b["CoLD ID"] ?? b.ID ?? "") as string;
      return aId.localeCompare(bId);
    });

  return sorted.map((item) => {
    const id = (item["CoLD ID"] ?? item.ID) as string;
    const level = typeof id === "string" ? id.match(/\./g)?.length || 0 : 0;

    // Backward compatible format for single jurisdiction
    if (isSingleJurisdiction.value) {
      const iso3 = jurisdictionCodes.value[0]?.toUpperCase();
      const answerText = (iso3 && answersMap.value?.[iso3]?.[id]) || "";
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
        const answerText = answersMap.value?.[iso3]?.[id] || "";
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
