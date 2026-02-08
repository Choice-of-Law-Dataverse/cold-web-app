<template>
  <UCard
    :ui="{
      body: '!p-0',
      header: 'border-b-0 px-4 py-5 sm:px-6',
    }"
  >
    <template #header>
      <div class="flex justify-between">
        <h3 class="comparison-title">Comparison</h3>
        <span class="flex flex-wrap gap-2">
          <UButton
            to="/learn/methodology"
            variant="outline"
            color="neutral"
            size="xs"
            icon="i-material-symbols:school-outline"
          >
            Methodology
          </UButton>
          <UButton
            to="/learn/glossary"
            variant="outline"
            color="neutral"
            size="xs"
            icon="i-material-symbols:dictionary-outline"
          >
            Glossary
          </UButton>
        </span>
      </div>
    </template>

    <div class="gradient-top-border" />

    <div class="flex flex-col gap-4 px-4 py-5 sm:px-6">
      <DetailRow label="Region">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="region in regions"
            :key="region"
            type="button"
            class="region-badge"
            :class="{ 'region-badge-active': selectedRegion === region }"
            @click="selectRegion(region)"
          >
            {{ region }}
          </button>
        </div>
      </DetailRow>

      <div v-if="isLoading" class="copy mt-4">Loading jurisdictions...</div>
      <div v-else-if="error" class="copy mt-4">Error loading jurisdictions</div>
      <div v-else class="flex flex-col gap-4">
        <DetailRow
          v-for="answer in answersWithJurisdictions"
          :key="answer"
          :label="answer"
        >
          <div class="flex flex-wrap items-center gap-4">
            <NuxtLink
              v-for="jurisdiction in getJurisdictionsForAnswer(answer)"
              :key="jurisdiction.code"
              class="label-jurisdiction"
              :to="`/question/${jurisdiction.code}${questionSuffix}`"
            >
              <div class="flag-wrapper">
                <JurisdictionFlag
                  :iso3="jurisdiction.code"
                  class="item-flag"
                  :alt="jurisdiction.code + ' flag'"
                />
              </div>

              {{ jurisdiction.code }}
            </NuxtLink>
          </div>
        </DetailRow>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import {
  useQuestionJurisdictions,
  type Jurisdiction,
} from "@/composables/useQuestionJurisdictions";
import DetailRow from "@/components/ui/DetailRow.vue";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";

const regions = [
  "All",
  "Asia & Pacific",
  "Europe",
  "Arab States",
  "Africa",
  "South & Latin America",
  "North America",
  "Middle East",
];

const props = defineProps<{
  questionSuffix: string;
}>();

const selectedRegion = ref("All");

const {
  data: questionData,
  isLoading,
  error,
} = useQuestionJurisdictions(computed(() => props.questionSuffix));

const answersWithJurisdictions = computed(() => {
  const answers = questionData.value?.answers || [];
  return answers.filter(
    (answer) => getJurisdictionsForAnswer(answer).length > 0,
  );
});

function selectRegion(region: string) {
  selectedRegion.value = region;
}

function getJurisdictionsForAnswer(answer: string): Jurisdiction[] {
  const jurisdictions = questionData.value?.answerGroups?.get(answer) || [];
  if (selectedRegion.value === "All") {
    return jurisdictions;
  }
  return jurisdictions.filter((j) => j.region === selectedRegion.value);
}
</script>

<style lang="sass" scoped></style>
