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
            <a
              v-for="jurisdiction in filteredAnswerGroups.get(answer)"
              :key="jurisdiction.code"
              class="label-jurisdiction"
              :href="`/question/${jurisdiction.code}${questionSuffix}`"
              @click="handleJurisdictionClick($event, jurisdiction.code)"
            >
              <div class="flag-wrapper">
                <JurisdictionFlag
                  :iso3="jurisdiction.code"
                  class="item-flag"
                  :alt="jurisdiction.code + ' flag'"
                />
              </div>

              {{ jurisdiction.code }}
            </a>
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
import { useEntityDrawer } from "@/composables/useEntityDrawer";
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

const { openDrawer } = useEntityDrawer();
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

function selectRegion(region: string) {
  selectedRegion.value = region;
}

function handleJurisdictionClick(event: MouseEvent, jurisdictionCode: string) {
  if (event.metaKey || event.ctrlKey) return;
  event.preventDefault();
  openDrawer(
    `${jurisdictionCode}${props.questionSuffix}`,
    "Answers",
    "/question",
  );
}
</script>

<style lang="sass" scoped></style>
