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

      <!-- Questions List -->
      <div v-else class="divide-y divide-cold-gray">
        <div
          v-for="row in rows"
          :id="`question-${row.id}`"
          :key="row.id"
          class="flex flex-col gap-2 py-3 md:flex-row md:items-center md:gap-4"
          :style="{ paddingLeft: `${row.level * 2}em` }"
        >
          <!-- Question -->
          <div class="whitespace-pre-line text-sm md:w-[60%]">
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
    </div>
  </UCard>
</template>

<script setup>
import { computed, useAttrs } from "vue";
import { useRoute } from "vue-router";
import { useQuestionsWithAnswers } from "@/composables/useQuestionsWithAnswers";
import LoadingBar from "@/components/layout/LoadingBar.vue";

const route = useRoute();

const {
  data: questionWithAnswersData,
  loading,
  answersLoading,
} = useQuestionsWithAnswers(computed(() => route?.params?.id));

const attrs = useAttrs();
const jurisdictionName = computed(() => {
  const name = attrs.formattedJurisdiction?.[0] || "";
  return name ? `for ${name}` : "";
});

const rows = computed(() => {
  if (
    !questionWithAnswersData.value ||
    !Array.isArray(questionWithAnswersData.value)
  ) {
    return [];
  }
  return questionWithAnswersData.value;
});
</script>
