<template>
  <UCard class="cold-ucard">
    <div class="flex flex-col gap-4">
      <div class="flex justify-between">
        <h3 class="comparison-title mb-4">Comparison</h3>
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
        <DetailRow v-for="answer in answers" :key="answer" :label="answer">
          <div
            v-if="getCountriesForAnswer(answer).length"
            class="flex flex-wrap items-center gap-4"
          >
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
                  @error="
                    (e) => {
                      e.target.style.display = 'none';
                    }
                  "
                />
              </div>

              {{ country.code }}
            </NuxtLink>
          </div>
          <div v-else class="copy">No jurisdictions</div>
        </DetailRow>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { ref, computed } from "vue";
import { useQuestionCountries } from "@/composables/useQuestionCountries";
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

const answers = computed(() => {
  const allAnswers = questionData.value?.answers || [];
  const uniqueAnswers = new Set(
    allAnswers
      .map((item) => item.Answer)
      .filter((answer) => typeof answer === "string" && answer.trim() !== ""),
  );

  const excludedAnswers = ["No data", "Nothing found", "No information"];
  excludedAnswers.forEach((answer) => uniqueAnswers.delete(answer));

  const priorityOrder = ["Yes", "No", "Not applicable"];
  const sortedAnswers = [];

  priorityOrder.forEach((answer) => {
    if (uniqueAnswers.has(answer)) {
      sortedAnswers.push(answer);
      uniqueAnswers.delete(answer);
    }
  });

  const remainingAnswers = Array.from(uniqueAnswers).sort((a, b) =>
    a.localeCompare(b),
  );
  sortedAnswers.push(...remainingAnswers);

  return sortedAnswers;
});

function selectRegion(region) {
  selectedRegion.value = region;
}

function getCountriesForAnswer(answer) {
  const allAnswers = questionData.value?.answers || [];

  let filtered = allAnswers.filter(
    (item) => typeof item.Answer === "string" && item.Answer === answer,
  );

  if (selectedRegion.value !== "All") {
    filtered = filtered.filter(
      (item) => item["Jurisdictions Region"] === selectedRegion.value,
    );
  }

  const countries = filtered
    .map((item) => ({
      name: item.Jurisdictions,
      code: item["Jurisdictions Alpha-3 code"],
    }))
    .sort((a, b) => a.name.localeCompare(b.name));

  return countries;
}
</script>

<style lang="sass" scoped></style>
