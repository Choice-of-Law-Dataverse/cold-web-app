<template>
  <UCard
    :ui="{
      body: '!p-0',
      header: 'border-b-0 px-4 py-5 sm:px-6',
    }"
  >
    <template #header>
      <div class="flex items-center justify-between">
        <h3 class="comparison-title">Comparison</h3>
        <span class="flex flex-wrap items-center gap-2">
          <USelect
            v-model="selectedRegion"
            :items="regions"
            size="xs"
            class="w-52"
            icon="i-material-symbols:globe"
          />
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

    <GradientTopBorder />

    <div class="flex flex-col gap-4 px-4 py-5 sm:px-6">
      <div v-if="isLoading" class="copy mt-4">Loading jurisdictions...</div>
      <div v-else-if="error" class="copy mt-4">Error loading jurisdictions</div>
      <div v-else class="flex flex-col gap-4">
        <DetailRow
          v-for="answer in answersWithJurisdictions"
          :key="answer"
          :label="answer"
        >
          <div class="flex flex-wrap items-center gap-4">
            <EntityLink
              v-for="jurisdiction in filteredAnswerGroups.get(answer)"
              :key="jurisdiction.code"
              :id="`${jurisdiction.code}${questionSuffix}`"
              :title="jurisdiction.code"
              base-path="/question"
              variant="jurisdiction"
            >
              <div class="flag-wrapper">
                <JurisdictionFlag
                  :iso3="jurisdiction.code"
                  class="item-flag"
                  :alt="jurisdiction.code + ' flag'"
                />
              </div>
              {{ jurisdiction.code }}
            </EntityLink>
          </div>
        </DetailRow>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import type { Jurisdiction } from "@/composables/useQuestionJurisdictions";
import { useQuestionJurisdictions } from "@/composables/useQuestionJurisdictions";
import DetailRow from "@/components/ui/DetailRow.vue";
import EntityLink from "@/components/ui/EntityLink.vue";
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

const filteredAnswerGroups = computed(() => {
  const groups = new Map<string, Jurisdiction[]>();
  for (const answer of questionData.value?.answers || []) {
    const all = questionData.value?.answerGroups?.get(answer) || [];
    const filtered =
      selectedRegion.value === "All"
        ? all
        : all.filter((j) => j.region === selectedRegion.value);
    if (filtered.length > 0) groups.set(answer, filtered);
  }
  return groups;
});

const answersWithJurisdictions = computed(() => [
  ...filteredAnswerGroups.value.keys(),
]);
</script>

<style lang="sass" scoped></style>
