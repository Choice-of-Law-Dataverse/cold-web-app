<template>
  <UCard class="cold-ucard">
    <div class="flex flex-col gap-6">
      <!-- Title Section -->
      <div>
        <h3 class="mb-1 text-left">Country Systematization</h3>
        <span class="result-value-small">
          View all jurisdictions for each answer to this question
        </span>
      </div>

      <!-- Answer Tabs -->
      <div>
        <h3 class="mb-4">
          <span
            v-for="option in answers"
            :key="option"
            class="answer-option mr-4 cursor-pointer"
            :class="{ 'selected-answer': selectedAnswer === option }"
            @click="selectAnswer(option)"
          >
            {{ option }}
          </span>
        </h3>

        <!-- Region Filter -->
        <p class="label regions-container mb-6 ml-1">
          <span
            v-for="region in regions"
            :key="region"
            class="region-label mr-4"
            :class="{ 'selected-region': selectedRegion === region }"
            style="cursor: pointer"
            @click="selectRegion(region)"
          >
            {{ region }}
          </span>
        </p>

        <!-- Jurisdictions Display -->
        <div v-if="selectedAnswer">
          <div v-if="isLoading" class="copy mt-4">
            Loading jurisdictions...
          </div>
          <div v-else-if="error" class="copy mt-4">
            Error loading jurisdictions
          </div>
          <div v-else-if="countries.length" class="countries-container mt-2">
            <NuxtLink
              v-for="country in countries"
              :key="country.code"
              class="country-item label-jurisdiction country-link-flex text-cold-purple"
              :to="`/question/${country.code}${questionSuffix}`"
            >
              <img
                :src="`https://choiceoflaw.blob.core.windows.net/assets/flags/${country.code?.toLowerCase()}.svg`"
                style="
                  height: 12px;
                  margin-right: 6px;
                  margin-bottom: 2px;
                "
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
          <div v-else class="copy mt-4">
            No jurisdictions to be displayed
          </div>
        </div>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { ref, computed } from "vue";
import { useQuestionCountries } from "@/composables/useQuestionCountries";

const answers = ["Yes", "No"];
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

const selectedAnswer = ref("Yes");
const selectedRegion = ref("All");

const {
  data: questionData,
  isLoading,
  error,
} = useQuestionCountries(
  computed(() => props.questionSuffix),
  selectedAnswer,
  selectedRegion,
);

const countries = computed(() => questionData.value?.countries || []);

function selectAnswer(answer) {
  selectedAnswer.value = answer;
}

function selectRegion(region) {
  selectedRegion.value = region;
}
</script>

<style scoped>
h3 {
  color: var(--color-cold-purple) !important;
}

.label {
  font-weight: 600 !important;
}

.label-jurisdiction {
  color: var(--color-cold-night) !important;
}

.regions-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.region-label {
  color: var(--color-cold-night-alpha-25);
}

.selected-region {
  color: inherit;
}

.countries-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}

.country-item {
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
}

.answer-option {
  padding-bottom: 2px;
  border-bottom: 2px solid transparent;
}

.selected-answer {
  border-bottom: 2px solid var(--color-cold-purple);
}
</style>
