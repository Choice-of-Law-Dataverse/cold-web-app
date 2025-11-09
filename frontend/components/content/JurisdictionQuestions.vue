<template>
  <UCard class="cold-ucard">
    <div class="overflow-hidden">
      <h2 class="mb-8 mt-2">Questions and Answers {{ jurisdictionName }}</h2>

      <!-- Loading State -->
      <div
        v-if="loading || answersLoading"
        class="flex flex-col space-y-3 py-8"
      >
        <LoadingBar />
        <LoadingBar />
        <LoadingBar />
      </div>

      <!-- Questions List - Single Jurisdiction -->
      <div v-else-if="isSingleJurisdiction" class="divide-y divide-cold-gray">
        <div
          v-for="row in rows"
          :id="`question-${row.id}`"
          :key="row.id"
          class="flex flex-col gap-2 py-3 md:flex-row md:items-center md:gap-4"
          :style="{ paddingLeft: `${row.level * 2}em` }"
        >
          <!-- Question -->
          <div class="whitespace-pre-line text-sm md:w-[60%]" :class="{ 'font-bold': isBoldQuestion(row.id) }">
            {{ row.question }}
          </div>

          <!-- Answer -->
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

      <!-- Questions List - Multiple Jurisdictions -->
      <div v-else>
        <!-- Desktop: Show headers for all jurisdictions -->
        <div class="hidden md:block">
          <div class="divide-y divide-cold-gray">
            <!-- Header Row -->
            <div class="flex gap-4 py-3 font-semibold border-b-2 border-cold-gray">
              <div class="w-[40%]">Question</div>
              <div v-for="jurisdiction in jurisdictions" :key="jurisdiction.alpha3Code || jurisdiction.Name" class="flex-1 text-center">
                {{ jurisdiction.Name }}
              </div>
            </div>
            <!-- Question Rows -->
            <div
              v-for="row in rows"
              :id="`question-${row.id}`"
              :key="row.id"
              class="flex gap-4 py-3"
              :style="{ paddingLeft: `${row.level * 2}em` }"
            >
              <!-- Question -->
              <div class="whitespace-pre-line text-sm w-[40%]" :class="{ 'font-bold': isBoldQuestion(row.id) }">
                {{ row.question }}
              </div>
              
              <!-- Answers for each jurisdiction -->
              <div v-for="jurisdiction in jurisdictions" :key="jurisdiction.alpha3Code || jurisdiction.Name" class="flex-1 text-center">
                <NuxtLink
                  v-if="jurisdiction.alpha3Code && row.answers?.[jurisdiction.alpha3Code]"
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

        <!-- Mobile: Show flag before answers -->
        <div class="block md:hidden divide-y divide-cold-gray">
          <div
            v-for="row in rows"
            :id="`question-${row.id}`"
            :key="row.id"
            class="py-3"
            :style="{ paddingLeft: `${row.level * 2}em` }"
          >
            <!-- Question -->
            <div class="whitespace-pre-line text-sm mb-3" :class="{ 'font-bold': isBoldQuestion(row.id) }">
              {{ row.question }}
            </div>
            
            <!-- Answers with flags for each jurisdiction -->
            <div class="flex flex-col gap-2">
              <div v-for="jurisdiction in jurisdictions" :key="jurisdiction.alpha3Code || jurisdiction.Name" class="flex items-center gap-2">
                <img 
                  v-if="jurisdiction.avatar" 
                  :src="jurisdiction.avatar" 
                  :alt="`${jurisdiction.Name} flag`"
                  class="w-6 h-4 object-cover"
                >
                <NuxtLink
                  v-if="jurisdiction.alpha3Code && row.answers?.[jurisdiction.alpha3Code]"
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
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useQuestionsWithAnswers, processAnswerText } from "@/composables/useQuestionsWithAnswers";
import LoadingBar from "@/components/layout/LoadingBar.vue";

// Props
const props = defineProps<{
  jurisdictions: Array<{
    Name: string;
    alpha3Code?: string;
    avatar?: string;
    [key: string]: unknown;
  }>;
}>();

// Hard-coded questions to render in bold
const BOLD_QUESTIONS = new Set(['03-PA', '07-PA', '08-PA', '09-FoC']);

const isBoldQuestion = (questionId: string) => {
  return BOLD_QUESTIONS.has(questionId);
};

// Extract alpha3 codes from jurisdictions
const jurisdictionCodes = computed(() => 
  props.jurisdictions.map(j => j.alpha3Code).filter((code): code is string => Boolean(code))
);

const {
  questionsData,
  answersMap,
  loading,
  answersLoading,
} = useQuestionsWithAnswers(jurisdictionCodes);

const isSingleJurisdiction = computed(() => props.jurisdictions.length === 1);

const jurisdictionName = computed(() => {
  if (isSingleJurisdiction.value) {
    return props.jurisdictions[0]?.Name ? `for ${props.jurisdictions[0].Name}` : "";
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

  const sorted = (questionsData.value as Array<{
    "CoLD ID"?: string;
    ID?: string;
    Question: string;
    Themes?: string;
    [key: string]: unknown;
  }>)
    .slice()
    .sort((a, b) => {
      const aId = (a["CoLD ID"] ?? a.ID ?? "") as string;
      const bId = (b["CoLD ID"] ?? b.ID ?? "") as string;
      return aId.localeCompare(bId);
    });

  return sorted.map((item) => {
    const id = (item["CoLD ID"] ?? item.ID) as string;
    const level = typeof id === "string" ? id.match(/\./g)?.length || 0 : 0;

    // For single jurisdiction, provide backward compatible format
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

    // For multiple jurisdictions, provide answers map
    const answers: Record<string, string> = {};
    for (const jurisdiction of props.jurisdictions) {
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
