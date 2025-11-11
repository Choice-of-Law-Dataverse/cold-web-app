<template>
  <div class="flex flex-col gap-4">
    <h4 class="label flex flex-wrap gap-4 text-lg">
      <span
        v-for="option in answers"
        :key="option"
        class="cursor-pointer border-b-2 border-transparent pb-0.5 hover:border-cold-teal"
        :class="
          selectedAnswer === option ? 'text-cold-teal' : 'text-cold-night'
        "
        @click="selectAnswer(option)"
      >
        {{ option }}
      </span>
    </h4>

    <p class="label flex flex-wrap gap-2">
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

    <div v-if="selectedAnswer">
      <div v-if="isLoading" class="copy mt-4">Loading jurisdictions...</div>
      <div v-else-if="error" class="copy mt-4">Error loading jurisdictions</div>
      <div
        v-else-if="countries.length"
        class="mt-2 flex flex-wrap items-center gap-3"
      >
        <NuxtLink
          v-for="country in countries"
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
      <div v-else class="copy mt-4">No jurisdictions</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useQuestionCountries } from "@/composables/useQuestionCountries";

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

<style scoped></style>
