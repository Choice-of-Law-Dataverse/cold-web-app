<template>
  <div>
    <!-- Desktop Layout -->
    <div class="hidden md:block">
      <div class="jc-grid jc-overview-row">
        <div class="jc-title-row flex items-center" style="grid-column: 1 / -1">
          <button
            v-if="showCaret"
            class="accordion-caret mr-2 mt-10"
            style="
              background: none;
              border: none;
              padding: 0;
              cursor: pointer;
              display: flex;
              align-items: center;
            "
            @click="isOpen = !isOpen"
          >
            <svg
              :style="{ transform: isOpen ? 'rotate(90deg)' : 'rotate(0deg)' }"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              width="16"
              height="16"
              fill="none"
              class="text-cold-purple"
            >
              <path
                d="M9 6l6 6-6 6"
                stroke="currentColor"
                stroke-width="3"
                stroke-linecap="square"
                stroke-linejoin="square"
              />
            </svg>
          </button>
          <h2 class="jc-title-fullwidth mb-6 mt-16">{{ title }}</h2>
        </div>
      </div>
      <hr class="jc-hr" >
      <div v-show="isOpen">
        <div v-if="isLoading" class="justify-left flex w-full py-8">
          <div class="w-full max-w-xs">
            <LoadingBar />
          </div>
        </div>
        <div
          v-else
          class="jc-table-grid"
          :class="{ 'cols-3': jurisdictionFilters.length === 3 }"
        >
          <div
            v-for="(label, i) in questionLabels"
            :key="'q-row-' + i"
            class="jc-table-row"
          >
            <div class="jc-table-cell jc-table-question result-value-medium">
              {{ label }}
            </div>
            <div
              v-for="j in jurisdictionFilters.length"
              :key="'a-' + i + '-' + j"
              class="jc-table-cell jc-table-answer result-value-large !pl-2 !pt-10"
            >
              <NuxtLink
                v-if="jurisdictionFilters[j - 1]?.value.value[0]?.alpha3Code"
                :to="`/question/${jurisdictionFilters[j - 1]?.value.value[0]?.alpha3Code?.toUpperCase()}_${questionIDs[i]}`"
                class="result-value-large"
              >
                {{ sampleData[j - 1]?.[i] || questionIDs[i] }}
              </NuxtLink>
              <span v-else>{{ sampleData[j - 1]?.[i] || questionIDs[i] }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile & Tablet Layout -->
    <div class="md:hidden">
      <div class="mobile-layout">
        <hr class="jc-hr mb-12 mt-4" >
        <div class="mb-2 mt-4 flex items-center">
          <button
            v-if="showCaret"
            class="accordion-caret mr-2"
            style="
              background: none;
              border: none;
              padding: 0;
              cursor: pointer;
              display: flex;
              align-items: center;
            "
            @click="isOpenMobile = !isOpenMobile"
          >
            <svg
              :style="{
                transform: isOpenMobile ? 'rotate(90deg)' : 'rotate(0deg)',
              }"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              width="16"
              height="16"
              fill="none"
              class="text-cold-purple"
            >
              <path
                d="M9 6l6 6-6 6"
                stroke="currentColor"
                stroke-width="3"
                stroke-linecap="square"
                stroke-linejoin="square"
              />
            </svg>
          </button>
          <h2 class="mt-0">{{ title }}</h2>
        </div>
        <div v-show="isOpenMobile" class="data-cards">
          <div v-if="isLoading" class="py-8">
            <div class="mobile-loading-wrapper">
              <LoadingBar />
            </div>
          </div>
          <div v-else>
            <div
              v-for="(label, i) in questionLabels"
              :key="'q-label-m-' + i"
              class="mb-8"
            >
              <p class="data-line-question mb-2 font-semibold">{{ label }}</p>
              <div
                v-for="(filter, index) in jurisdictionFilters"
                :key="`mobile-q-${i}-j-${index}`"
                class="mb-4"
              >
                <h3 class="data-card-title mb-1 flex items-center">
                  <template
                    v-if="
                      filter.value.value.length > 0 &&
                      filter.value.value[0]?.label !== 'All Jurisdictions'
                    "
                  >
                    <img
                      v-if="
                        !erroredFlags[index] &&
                        getFlagUrl(filter.value.value[0].label)
                      "
                      :src="getFlagUrl(filter.value.value[0].label)"
                      style="
                        height: 18px;
                        width: auto;
                        margin-right: 0.5em;
                        border-radius: 0;
                        border: 1px solid var(--color-cold-gray);
                      "
                      :alt="filter.value.value[0].label + ' flag'"
                      @error="() => (erroredFlags[index] = true)"
                    >
                    {{ filter.value.value[0].label }}
                  </template>
                  <template v-else>
                    {{ `Jurisdiction ${index + 1}` }}
                  </template>
                </h3>
                <div class="data-card-content result-value-large">
                  <p class="data-line">
                    <NuxtLink
                      v-if="filter?.value.value[0]?.alpha3Code"
                      :to="`/question/${filter?.value.value[0]?.alpha3Code?.toUpperCase()}_${questionIDs[i]}`"
                      class="result-value-large"
                    >
                      {{ sampleData[index]?.[i] || questionIDs[i] }}
                    </NuxtLink>
                    <span v-else>{{
                      sampleData[index]?.[i] || questionIDs[i]
                    }}</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import { useJurisdictionComparison } from "@/composables/useJurisdictionComparison";
import { useJurisdictions } from "@/composables/useJurisdictions";

const props = defineProps({
  showCaret: {
    type: Boolean,
    default: true,
  },
  title: {
    type: String,
    default: "Please Set Title",
  },
  questionIDs: {
    type: Array,
    required: false,
    default: () => [],
  },
});

const isOpen = ref(false);
const isOpenMobile = ref(false);
const hasBeenOpened = ref(false);

watch(
  () => props.showCaret,
  (val) => {
    if (!val) {
      isOpen.value = true;
      isOpenMobile.value = true;
      hasBeenOpened.value = true;
    }
  },
  { immediate: true },
);

watch([isOpen, isOpenMobile], ([desktop, mobile]) => {
  if ((desktop || mobile) && !hasBeenOpened.value) {
    hasBeenOpened.value = true;
    loadAccordionData();
  }
});

const { data: jurisdictions } = useJurisdictions();

const { jurisdictionFilters } = useJurisdictionComparison();

const erroredFlags = ref({});

const getFlagUrl = (label) => {
  if (!label || label === "All Jurisdictions") return "";
  const found = jurisdictions.value.find((j) => j.label === label);
  if (found?.avatar) return found.avatar;
  return `https://choiceoflaw.blob.core.windows.net/assets/flags/${label.toLowerCase()}.svg`;
};

const questionLabels = ref([]);
const loadingQuestions = ref(false);

const answersData = ref({});
const loadingAnswers = ref(false);

const isLoading = computed(
  () => hasBeenOpened.value && (loadingQuestions.value || loadingAnswers.value),
);

const fetchQuestions = async () => {
  if (!hasBeenOpened.value) return;

  try {
    const promises = props.questionIDs.map(async (id) => {
      try {
        const response = await fetch(`/api/proxy/search/full_table`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            table: "Questions",
            filters: [{ column: "ID", value: id }],
          }),
        });

        if (!response.ok) return id;

        const data = await response.json();
        return data[0]?.Question || id;
      } catch {
        return id;
      }
    });

    questionLabels.value = await Promise.all(promises);
  } catch (error) {
    console.error("Error fetching questions:", error);
    questionLabels.value = props.questionIDs;
  }
  // Note: Don't set loadingQuestions to false here - let loadAccordionData handle it
};

const fetchAnswerData = async (id) => {
  if (!id || answersData.value[id] !== undefined) {
    return answersData.value[id];
  }

  try {
    const response = await fetch(`/api/proxy/search/details`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ table: "Answers", id }),
    });

    if (!response.ok) {
      answersData.value[id] = null;
      return null;
    }

    const data = await response.json();
    const answer = data?.Answer || null;
    answersData.value[id] = answer;
    return answer;
  } catch (error) {
    console.error(`Error fetching answer for ${id}:`, error);
    answersData.value[id] = null;
    return null;
  }
};

const fetchAllAnswers = async () => {
  if (
    !hasBeenOpened.value ||
    !jurisdictionFilters.value.length ||
    !props.questionIDs.length
  )
    return;

  const promises = jurisdictionFilters.value.flatMap((filter) => {
    const alpha3Code = filter.value.value[0]?.alpha3Code?.toUpperCase();
    if (!alpha3Code) return [];

    return props.questionIDs.map((questionID) =>
      fetchAnswerData(`${alpha3Code}_${questionID}`),
    );
  });

  await Promise.all(promises);
  // Note: Don't set loadingAnswers to false here - let loadAccordionData handle it
};

const loadAccordionData = async () => {
  loadingQuestions.value = true;
  loadingAnswers.value = true;

  try {
    await Promise.all([fetchQuestions()]);
    await fetchAllAnswers();
  } finally {
    loadingQuestions.value = false;
    loadingAnswers.value = false;
  }
};

watch(
  [jurisdictionFilters, () => props.questionIDs],
  async () => {
    if (hasBeenOpened.value) {
      loadingAnswers.value = true;
      try {
        await fetchAllAnswers();
      } finally {
        loadingAnswers.value = false;
      }
    }
  },
  { deep: true },
);

const sampleData = computed(() => {
  if (!hasBeenOpened.value) return [];

  return jurisdictionFilters.value.map((filter) => {
    const alpha3Code = filter.value.value[0]?.alpha3Code?.toUpperCase();

    return props.questionIDs.map((questionID) => {
      if (!alpha3Code) return questionID;

      const id = `${alpha3Code}_${questionID}`;
      const answer = answersData.value[id];

      if (answer !== undefined) {
        return answer !== null
          ? answer
          : `No answer available for ${questionID}`;
      }

      return questionID;
    });
  });
});

onMounted(async () => {
  if (!props.showCaret) {
    hasBeenOpened.value = true;
    await loadAccordionData();
  }
});
</script>

<style scoped>
.mobile-loading-wrapper {
  max-width: 200px !important;
  width: 100% !important;
  margin: 0;
  overflow: hidden !important;
}

.mobile-loading-wrapper :deep(*),
.mobile-loading-wrapper :deep(.space-y-2),
.mobile-loading-wrapper :deep(.h-2) {
  max-width: 100% !important;
  width: 100% !important;
}

.jc-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr 1fr;
  align-items: start;
  gap: 0 0.25rem;
}

.jc-table-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0 0.25rem;
  width: 100%;
}

.jc-table-grid.cols-3 {
  grid-template-columns: 1fr 1fr 1fr 1fr;
}

.jc-table-row {
  display: contents;
}

.jc-table-cell {
  padding: 0.75rem 0;
  vertical-align: top;
  font-size: 1rem;
}

.jc-table-question {
  font-weight: 400;
  white-space: pre-line;
}

.jc-table-answer {
  text-align: left;
  font-weight: 400;
}

.mobile-layout {
  padding: 0.25rem;
}

.mobile-layout .flex {
  max-width: 100% !important;
  width: 100% !important;
  justify-content: left;
  align-items: left;
}

.data-cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

.data-card-title {
  font-weight: 600;
  font-size: 1.125rem;
  margin-bottom: 1rem;
  color: var(--color-cold-purple);
}

.data-line {
  margin-bottom: 1.5rem;
  line-height: 1.3em;
}

.data-line-question {
  margin-bottom: 1.5rem;
  margin-top: 4rem;
  line-height: 1.6em;
}

.result-value-medium {
  font-weight: 400 !important;
  margin-top: 32px !important;
}

.jc-title-fullwidth {
  grid-column: 1 / -1 !important;
}

.jc-search-filter :deep(.cold-uselectmenu) {
  width: 270px !important;
}

.jc-mobile-filters-container,
.jc-mobile-data-container {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  padding: 1rem 0;
  scrollbar-width: thin;
  scrollbar-color: var(--color-cold-gray) transparent;
}

.jc-mobile-filters-container::-webkit-scrollbar,
.jc-mobile-data-container::-webkit-scrollbar {
  height: 6px;
}
</style>
