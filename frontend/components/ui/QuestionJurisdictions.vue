<template>
  <UCard class="cold-ucard">
    <div class="flex flex-col gap-4">
      <div class="flex justify-between">
        <h3 class="comparison-title mb-4 text-xl font-semibold md:text-2xl">
          Comparison
        </h3>
        <span class="mb-4 flex flex-wrap gap-2">
          <NuxtLink to="/learn/methodology" type="button" class="action-button">
            <UIcon
              :name="'i-material-symbols:school-outline'"
              class="inline-block text-[1.2em]"
            />
            Methodology
          </NuxtLink>
          <NuxtLink to="/learn/glossary" type="button" class="action-button">
            <UIcon
              :name="'i-material-symbols:dictionary-outline'"
              class="inline-block text-[1.2em]"
            />
            Glossary
          </NuxtLink>
        </span>
      </div>

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
              v-for="country in getCountriesForAnswer(answer)"
              :key="country.code"
              class="label-jurisdiction"
              :to="`/question/${country.code}${questionSuffix}`"
            >
              <div class="flag-wrapper">
                <img
                  :src="`https://choiceoflaw.blob.core.windows.net/assets/flags/${country.code?.toLowerCase()}.svg`"
                  class="item-flag"
                  :alt="country.code + ' flag'"
                />
              </div>

              {{ country.code }}
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
  useQuestionCountries,
  type Country,
} from "@/composables/useQuestionCountries";
import DetailRow from "@/components/ui/DetailRow.vue";

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
} = useQuestionCountries(computed(() => props.questionSuffix));

const answersWithJurisdictions = computed(() => {
  const answers = questionData.value?.answers || [];
  return answers.filter((answer) => getCountriesForAnswer(answer).length > 0);
});

function selectRegion(region: string) {
  selectedRegion.value = region;
}

function getCountriesForAnswer(answer: string): Country[] {
  const countries = questionData.value?.answerGroups?.get(answer) || [];
  if (selectedRegion.value === "All") {
    return countries;
  }
  return countries.filter((c) => c.region === selectedRegion.value);
}
</script>

<style lang="sass" scoped></style>
