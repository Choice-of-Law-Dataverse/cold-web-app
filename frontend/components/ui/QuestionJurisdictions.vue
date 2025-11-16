<template>
  <div class="w-full">
    <h3 class="label mb-4 text-2xl font-semibold">Comparison</h3>

    <p class="label mb-4 flex flex-wrap gap-2">
      <span
        v-for="region in regions"
        :key="region"
        class="cursor-pointer border-b-2 border-transparent pb-0.5 hover:border-cold-teal"
        :class="
          selectedRegion === region ? 'text-cold-teal' : 'text-cold-night'
        "
        @click="selectRegion(region)"
      >
        {{ region }}
      </span>
    </p>

    <div v-if="isLoading" class="copy mt-4">Loading jurisdictions...</div>
    <div v-else-if="error" class="copy mt-4">Error loading jurisdictions</div>
    <div v-else class="flex flex-col gap-6">
      <DetailRow
        v-for="answer in answers"
        :key="answer"
        :label="answer"
      >
        <div
          v-if="getCountriesForAnswer(answer).length"
          class="flex flex-wrap items-center gap-3"
        >
          <NuxtLink
            v-for="country in getCountriesForAnswer(answer)"
            :key="country.code"
            class="label-jurisdiction inline-flex items-center whitespace-nowrap text-cold-night hover:text-cold-purple"
            :to="`/question/${country.code}${questionSuffix}`"
          >
            <img
              :src="`https://choiceoflaw.blob.core.windows.net/assets/flags/${country.code?.toLowerCase()}.svg`"
              class="mb-0.5 mr-1.5 h-3"
              :alt="country.code + ' flag'"
              @error="
                (e) => {
                  e.target.style.display = 'none';
                }
              "
            >
            {{ country.name }}
          </NuxtLink>
        </div>
        <div v-else class="copy">No jurisdictions</div>
      </DetailRow>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useQuestionCountries } from "@/composables/useQuestionCountries";
import DetailRow from "@/components/ui/DetailRow.vue";

const answers = ["Yes", "No", "Not applicable"];
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

const props = defineProps({
  questionSuffix: {
    type: String,
    required: true,
  },
});

const selectedRegion = ref("All");

const {
  data: questionData,
  isLoading,
  error,
} = useQuestionCountries(computed(() => props.questionSuffix));

function selectRegion(region) {
  selectedRegion.value = region;
}

function getCountriesForAnswer(answer) {
  const allAnswers = questionData.value?.answers || [];

  // Filter by answer
  let filtered = allAnswers.filter(
    (item) => typeof item.Answer === "string" && item.Answer === answer,
  );

  // Filter by region if not "All"
  if (selectedRegion.value !== "All") {
    filtered = filtered.filter(
      (item) => item["Jurisdictions Region"] === selectedRegion.value,
    );
  }

  // Map to country objects and sort
  const countries = filtered
    .map((item) => ({
      name: item.Jurisdictions,
      code: item["Jurisdictions Alpha-3 code"],
    }))
    .sort((a, b) => a.name.localeCompare(b.name));

  return countries;
}
</script>

<style scoped></style>
