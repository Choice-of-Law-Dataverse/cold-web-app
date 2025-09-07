<template>
  <div>
    <!-- Desktop Layout -->
    <div class="hidden md:block">
      <div class="jc-grid jc-overview-row">
        <div class="jc-title-row flex items-center" style="grid-column: 1 / -1">
          <button
            v-if="showCaret"
            @click="isOpen = !isOpen"
            class="accordion-caret mr-2 mt-10"
            style="
              background: none;
              border: none;
              padding: 0;
              cursor: pointer;
              display: flex;
              align-items: center;
            "
          >
            <svg
              :style="{ transform: isOpen ? 'rotate(90deg)' : 'rotate(0deg)' }"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              width="16"
              height="16"
              fill="none"
              style="color: var(--color-cold-purple)"
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
          <h2 class="mt-16 mb-6 jc-title-fullwidth">{{ title }}</h2>
        </div>
      </div>
      <hr class="jc-hr" />
      <div v-show="isOpen">
        <div v-if="isLoading" class="flex justify-left py-8 w-full">
          <div class="w-full max-w-xs">
            <LoadingBar />
          </div>
        </div>
        <div v-else class="jc-table-grid">
          <div
            v-for="(label, i) in questionLabels"
            :key="'q-row-' + i"
            class="jc-table-row"
          >
            <div class="jc-table-cell jc-table-question result-value-medium">
              {{ label }}
            </div>
            <div
              v-for="j in 3"
              :key="'a-' + i + '-' + j"
              class="jc-table-cell jc-table-answer result-value-large !pt-10 !pl-2"
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
        <hr class="jc-hr mt-4 mb-12" />
        <div class="flex items-center mb-2 mt-4">
          <button
            v-if="showCaret"
            @click="isOpenMobile = !isOpenMobile"
            class="accordion-caret mr-2"
            style="
              background: none;
              border: none;
              padding: 0;
              cursor: pointer;
              display: flex;
              align-items: center;
            "
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
              style="color: var(--color-cold-purple)"
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
              <p class="data-line-question font-semibold mb-2">{{ label }}</p>
              <div
                v-for="(filter, index) in jurisdictionFilters"
                :key="`mobile-q-${i}-j-${index}`"
                class="mb-4"
              >
                <h3 class="data-card-title flex items-center mb-1">
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
                      @error="() => (erroredFlags[index] = true)"
                      style="
                        height: 18px;
                        width: auto;
                        margin-right: 0.5em;
                        border-radius: 0;
                        border: 1px solid var(--color-cold-gray);
                      "
                      :alt="filter.value.value[0].label + ' flag'"
                    />
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
import { ref, computed, onMounted, watch } from 'vue'
import LoadingBar from '@/components/layout/LoadingBar.vue'
import { useJurisdictionComparison } from '@/composables/useJurisdictionComparison'

const props = defineProps({
  showCaret: {
    type: Boolean,
    default: true,
  },
  title: {
    type: String,
    default: 'Please Set Title',
  },
  questionIDs: {
    type: Array,
    required: true,
    default: () => [],
  },
})

// Accordion state
const isOpen = ref(false)
const isOpenMobile = ref(false)
const hasBeenOpened = ref(false)

// Always force open if showCaret is false
watch(
  () => props.showCaret,
  (val) => {
    if (!val) {
      isOpen.value = true
      isOpenMobile.value = true
      hasBeenOpened.value = true
    }
  },
  { immediate: true }
)

// Track when accordion is opened for the first time
watch([isOpen, isOpenMobile], ([desktop, mobile]) => {
  if ((desktop || mobile) && !hasBeenOpened.value) {
    hasBeenOpened.value = true
    // Start loading data when first opened
    loadAccordionData()
  }
})

const { data: jurisdictions } = useJurisdictions()

// Use shared jurisdiction comparison state
const { jurisdictionFilters } = useJurisdictionComparison()

// Track errored flag images
const erroredFlags = ref({})

// Flag URL helper function
const getFlagUrl = (label) => {
  if (!label || label === 'All Jurisdictions') return ''
  const found = jurisdictions.value.find((j) => j.label === label)
  if (found?.avatar) return found.avatar
  return `https://choiceoflaw.blob.core.windows.net/assets/flags/${label.toLowerCase()}.svg`
}

// Questions state
const questionLabels = ref([])
const loadingQuestions = ref(false) // Start as false, only set to true when actually loading

// Answers state
const answersData = ref({})
const loadingAnswers = ref(false)

// Combined loading state - only load when accordion has been opened
const isLoading = computed(
  () => hasBeenOpened.value && (loadingQuestions.value || loadingAnswers.value)
)

// API configuration
const getApiConfig = () => {
  const config = useRuntimeConfig()
  return {
    baseUrl: config.public.apiBaseUrl,
    headers: {
      Authorization: `Bearer ${config.public.FASTAPI}`,
      'Content-Type': 'application/json',
    },
  }
}

// Fetch questions with improved error handling
const fetchQuestions = async () => {
  if (!hasBeenOpened.value) return // Don't fetch if accordion hasn't been opened

  const { baseUrl, headers } = getApiConfig()

  try {
    const promises = props.questionIDs.map(async (id) => {
      try {
        const response = await fetch(`${baseUrl}/search/full_table`, {
          method: 'POST',
          headers,
          body: JSON.stringify({
            table: 'Questions',
            filters: [{ column: 'ID', value: id }],
          }),
        })

        if (!response.ok) return id

        const data = await response.json()
        return data[0]?.Question || id
      } catch {
        return id
      }
    })

    questionLabels.value = await Promise.all(promises)
  } catch (error) {
    console.error('Error fetching questions:', error)
    questionLabels.value = props.questionIDs
  }
  // Note: Don't set loadingQuestions to false here - let loadAccordionData handle it
}

// Fetch answer data with caching
const fetchAnswerData = async (id) => {
  if (!id || answersData.value[id] !== undefined) {
    return answersData.value[id]
  }

  const { baseUrl, headers } = getApiConfig()
  console.log('[JCQuestions.vue] fetchAnswerData id:', id)

  try {
    const response = await fetch(`${baseUrl}/search/details`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ table: 'Answers', id }),
    })

    if (!response.ok) {
      answersData.value[id] = null
      return null
    }

    const data = await response.json()
    const answer = data?.Answer || null
    answersData.value[id] = answer
    return answer
  } catch (error) {
    console.error(`Error fetching answer for ${id}:`, error)
    answersData.value[id] = null
    return null
  }
}

// Fetch all answers for current jurisdictions and questions
const fetchAllAnswers = async () => {
  if (
    !hasBeenOpened.value ||
    !jurisdictionFilters.value.length ||
    !props.questionIDs.length
  )
    return

  const promises = jurisdictionFilters.value.flatMap((filter) => {
    const alpha3Code = filter.value.value[0]?.alpha3Code?.toUpperCase()
    if (!alpha3Code) return []

    return props.questionIDs.map((questionID) =>
      fetchAnswerData(`${alpha3Code}_${questionID}`)
    )
  })

  await Promise.all(promises)
  // Note: Don't set loadingAnswers to false here - let loadAccordionData handle it
}

// Load accordion data when opened
const loadAccordionData = async () => {
  // Set loading state for both questions and answers
  loadingQuestions.value = true
  loadingAnswers.value = true

  try {
    // Load jurisdictions and questions in parallel
    await Promise.all([fetchQuestions()])
    // Then load answers (which depends on jurisdictions being loaded)
    await fetchAllAnswers()
  } finally {
    // Ensure loading states are cleared even if there's an error
    loadingQuestions.value = false
    loadingAnswers.value = false
  }
}

// Watch for changes and refetch data (only if accordion has been opened)
watch(
  [jurisdictionFilters, () => props.questionIDs],
  async () => {
    if (hasBeenOpened.value) {
      loadingAnswers.value = true
      try {
        await fetchAllAnswers()
      } finally {
        loadingAnswers.value = false
      }
    }
  },
  { deep: true }
)

// Computed answer data
const sampleData = computed(() => {
  if (!hasBeenOpened.value) return [] // Return empty array if not opened yet

  return jurisdictionFilters.value.map((filter) => {
    const alpha3Code = filter.value.value[0]?.alpha3Code?.toUpperCase()

    return props.questionIDs.map((questionID) => {
      if (!alpha3Code) return questionID

      const id = `${alpha3Code}_${questionID}`
      const answer = answersData.value[id]

      if (answer !== undefined) {
        return answer !== null
          ? answer
          : `No answer available for ${questionID}`
      }

      return questionID
    })
  })
})

// Initialization - only load jurisdictions initially, not questions/answers
onMounted(async () => {
  // If showCaret is false, immediately load data since accordion should be open
  if (!props.showCaret) {
    hasBeenOpened.value = true
    await loadAccordionData()
  }
})
</script>

<style scoped>
/* Loading components */
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

/* Grid layouts */
.jc-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr 1fr;
  align-items: start;
  gap: 0 1.5rem;
}

.jc-table-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 0 1.5rem;
  width: 100%;
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

/* Mobile layout */
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

/* Utility classes */
.result-value-medium {
  font-weight: 400 !important;
  margin-top: 32px !important;
}

.jc-title-fullwidth {
  grid-column: 1 / -1 !important;
}

/* Component-specific styles */
.jc-search-filter :deep(.cold-uselectmenu) {
  width: 270px !important;
}

/* Scrollbar styles */
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
