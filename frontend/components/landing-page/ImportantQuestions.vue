<template>
  <div class="important-questions-wrapper relative">
    <div class="card-container">
      <div class="card-inner">
        <button
          class="nav-button-outside left"
          aria-label="Previous question"
          @click="prevQuestion"
          type="button"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            height="24"
            fill="none"
            style="transform: rotate(180deg); color: var(--color-cold-purple)"
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
        <UCard class="cold-ucard">
          <div class="popular-searches-container flex flex-col gap-8">
            <div>
              <div class="flex items-center justify-center md:justify-between">
                <h2
                  ref="titleRef"
                  class="popular-title text-center md:text-left mb-0"
                >
                  {{ questionTitle || 'Missing Question' }}
                </h2>
              </div>
              <div>
                <h3 class="mt-4">
                  <span
                    v-for="(option, idx) in answers"
                    :key="option"
                    class="mr-4 cursor-pointer answer-option"
                    :class="{ 'selected-answer': selectedAnswer === option }"
                    @click="selectAnswer(option)"
                  >
                    {{ option }}
                  </span>
                </h3>
                <div style="position: relative">
                  <p class="label mt-6 mb-6 ml-1 regions-scroll">
                    <span
                      v-for="(region, idx) in regions"
                      :key="region"
                      class="mr-4 region-label"
                      :class="{ 'selected-region': selectedRegion === region }"
                      style="cursor: pointer"
                      @click="selectRegion(region)"
                    >
                      {{ region }}
                    </span>
                  </p>
                  <div class="fade-out fade-out-region"></div>
                  <!-- left-side fade (mirror of the right-side) -->
                  <div class="fade-out fade-out-region fade-out-left"></div>
                </div>
                <div v-if="selectedAnswer">
                  <div
                    v-if="countries.length"
                    class="countries-scroll mt-2 countries-scroll-fade-container"
                    style="position: relative"
                  >
                    <div class="countries-lines">
                      <div
                        class="countries-line"
                        v-for="(line, li) in countriesLines"
                        :key="li"
                      >
                        <a
                          v-for="country in line"
                          :key="country.code"
                          class="country-item label-jurisdiction country-link-flex"
                          :href="`/question/${country.code}${currentSuffix}`"
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
                                e.target.style.display = 'none'
                              }
                            "
                          />
                          {{ country.name }}
                        </a>
                      </div>
                    </div>
                    <div
                      class="fade-out fade-out-countries countries-fade-fixed"
                    ></div>
                    <!-- left-side fade for countries -->
                    <div
                      class="fade-out fade-out-countries countries-fade-fixed-left"
                    ></div>
                  </div>
                  <div v-else class="mt-4 copy">
                    No jurisdictions to be displayed
                  </div>
                </div>
              </div>
            </div>
          </div>
        </UCard>
        <button
          class="nav-button-outside right"
          aria-label="Next question"
          @click="nextQuestion"
          type="button"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            height="24"
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
      </div>
      <!-- Dots navigation -->
      <div class="dots-outside w-full flex justify-center">
        <div class="carousel-dots flex justify-center gap-2">
          <button
            v-for="(suf, idx) in suffixes"
            :key="idx"
            @click="((currentIndex = idx), fetchCountries())"
            :aria-label="`Go to question ${idx + 1}`"
            :class="['dot', { 'dot-active': currentIndex === idx }]"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue'
import { useRuntimeConfig } from '#imports'

const answers = ['Yes', 'No']
const regions = [
  'All',
  'Asia & Pacific',
  'Europe',
  'Arab States',
  'Africa',
  'South & Latin America',
  'North America',
  'Middle East',
]

const selectedAnswer = ref('Yes')
const selectedRegion = ref('All')
const countries = ref([])
const countriesLines = ref([])
const questionTitle = ref('')
const titleRef = ref(null)
const rowsCount = ref(3)
// Carousel: accept an array of question suffixes to rotate through
const props = defineProps({
  questionSuffixes: {
    type: Array,
    default: () => ['_01-P'],
  },
})

const currentIndex = ref(0)
const suffixes = computed(() => props.questionSuffixes)
const totalQuestions = computed(() => suffixes.value.length)
const currentSuffix = computed(() => suffixes.value[currentIndex.value])

const prevQuestion = () => {
  currentIndex.value =
    (currentIndex.value - 1 + totalQuestions.value) % totalQuestions.value
  fetchCountries()
}

const nextQuestion = () => {
  currentIndex.value = (currentIndex.value + 1) % totalQuestions.value
  fetchCountries()
}

const config = useRuntimeConfig()

async function fetchCountries() {
  if (!selectedAnswer.value) {
    countries.value = []
    return
  }
  try {
    const res = await fetch(`/api/proxy/search/full_table`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        table: 'Answers',
        // Ask backend for rows where ID contains the suffix; we'll enforce endsWith on the client
        filters: [
          { column: 'ID', value: currentSuffix.value },
          { column: 'Answer', value: selectedAnswer.value },
        ],
      }),
    })
    if (!res.ok) throw new Error('API error')
    const data = await res.json()
    // Ensure we only keep rows whose ID actually ends with the requested suffix
    const dataWithSuffix = Array.isArray(data)
      ? data.filter(
          (item) =>
            typeof item.ID === 'string' && item.ID.endsWith(currentSuffix.value)
        )
      : []

    // Enforce exact match on the Answer field (API may do substring matching)
    const exactAnswerMatches = dataWithSuffix.filter(
      (item) =>
        typeof item.Answer === 'string' && item.Answer === selectedAnswer.value
    )

    // Populate questionTitle from an exact-answer match if available, otherwise fall back
    if (
      exactAnswerMatches.length > 0 &&
      typeof exactAnswerMatches[0].Question === 'string'
    ) {
      questionTitle.value = exactAnswerMatches[0].Question
    } else if (
      dataWithSuffix.length > 0 &&
      typeof dataWithSuffix[0].Question === 'string'
    ) {
      questionTitle.value = dataWithSuffix[0].Question
    }

    // Start from exact-answer matches so "No" does not match "No Data"
    let filtered = exactAnswerMatches.filter(
      (item) => item['Jurisdictions Irrelevant'] !== 'Yes'
    )
    if (selectedRegion.value !== 'All') {
      filtered = filtered.filter(
        (item) => item['Jurisdictions Region'] === selectedRegion.value
      )
    }
    // Map to objects with name and code, then sort by name
    const list = filtered
      .map((item) => ({
        name: item.Jurisdictions,
        code: item['Jurisdictions Alpha-3 code'],
      }))
      .sort((a, b) => a.name.localeCompare(b.name))
    countries.value = list
    // after DOM updates, measure title and compute rows, then split
    await nextTick()
    computeRows()
    countriesLines.value = splitIntoLines(list, rowsCount.value)
  } catch (e) {
    countries.value = ['Error loading countries']
    countriesLines.value = [['Error loading countries']]
  }
}

function selectAnswer(answer) {
  selectedAnswer.value = answer
  fetchCountries()
}

function selectRegion(region) {
  selectedRegion.value = region
  fetchCountries()
}

onMounted(() => {
  fetchCountries()
  // compute rows on mount and on resize
  computeRows()
  window.addEventListener('resize', computeRows)
})

// Cleanup resize listener when component unmounts
onUnmounted(() => {
  window.removeEventListener('resize', computeRows)
})

function computeRows() {
  // Measure rendered title height to determine how many text lines it takes.
  // If the title occupies 1 line, allow 4 country rows; otherwise keep 3.
  const el = titleRef.value
  if (!el) {
    rowsCount.value = 3
    return
  }
  try {
    const style = getComputedStyle(el)
    const lineHeight = parseFloat(style.lineHeight)
    const height = el.offsetHeight
    if (lineHeight > 0 && height > 0) {
      const lines = Math.round(height / lineHeight) || 1
      rowsCount.value = lines <= 1 ? 4 : 3
    } else {
      rowsCount.value = 3
    }
  } catch (err) {
    rowsCount.value = 3
  }
}

function splitIntoLines(items, rows) {
  // Split already-sorted items into `rows` contiguous rows with equal counts when possible.
  const n = items.length
  if (n === 0) return Array.from({ length: rows }, () => [])
  const base = Math.floor(n / rows)
  const rem = n % rows
  const sizes = Array.from({ length: rows }, (_, i) => base + (i < rem ? 1 : 0))
  const out = []
  let idx = 0
  for (let i = 0; i < rows; i++) {
    const size = sizes[i]
    out.push(items.slice(idx, idx + size))
    idx += size
  }
  return out
}
</script>

<style scoped>
.label {
  font-weight: 600 !important;
}

.label-jurisdiction {
  color: var(--color-cold-night) !important;
}

.regions-scroll {
  overflow-x: auto;
  white-space: nowrap;
  display: block;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}
.regions-scroll::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.countries-scroll {
  overflow-x: hidden; /* outer acts as viewport */
  overflow-y: hidden;
  position: relative;
}

.countries-scroll-fade-container {
  --fade-width: 20px;
  --scroll-padding-buffer: 100px; /* space to clear fade */
  --scroll-tail-buffer: 200px; /* extra empty space AFTER last item */
}

.countries-lines {
  display: flex;
  flex-direction: column;
  gap: 0.75em; /* tighter horizontal spacing within each row */
  overflow-x: auto; /* actual horizontal scroll container */
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding-right: calc(var(--fade-width) + var(--scroll-padding-buffer));
  margin-right: 0 !important;
}

.countries-lines::-webkit-scrollbar {
  display: none;
}

/* Spacer to allow final country to clear the fade overlay */
.countries-lines::after {
  content: '';
  flex: 0 0 auto;
  width: calc(var(--fade-width) + var(--scroll-tail-buffer));
  height: 1px;
}

.countries-line {
  display: inline-flex;
  gap: 0.1em;
}

/* Remove obsolete element-based spacer styles (end-spacer div removed) */
.end-spacer {
  display: none;
}
.region-label {
  color: var(--color-cold-night-alpha-25);
}
.selected-region {
  color: inherit;
}
.fade-out {
  position: absolute;
  top: 0;
  right: 0;
  width: 60px;
  height: 100%;
  background: linear-gradient(to left, white, transparent);
  pointer-events: none;
  z-index: 10;
}
.fade-out-region {
  height: 2.2em;
  right: 0;
}
.fade-out-countries {
  height: 100%;
  right: 0;
}
/* Left-side fades mirror the right-side fades but anchored to the left */
.fade-out-left {
  /* mirror right-side fade but anchored left and narrower */
  left: 0;
  right: auto;
  top: 0;
  width: 8px; /* narrower left fade */
  height: 100%;
  pointer-events: none;
  z-index: 10;
  background: linear-gradient(to right, white, transparent);
}
.countries-fade-fixed-left {
  left: 0;
  right: auto;
  top: 0;
  width: 8px; /* match left fade width */
  height: 100%;
  pointer-events: none;
  z-index: 10;
  background: linear-gradient(to right, white, transparent);
}
.countries-scroll-fade-container {
  position: relative;
  overflow: hidden; /* Ensure the fade-out stays fixed */
}
.countries-lines {
  overflow-x: auto; /* Allow scrolling within the container */
}
.countries-fade-fixed {
  position: absolute;
  top: 0;
  right: 0;
  width: 60px;
  height: 100%;
  pointer-events: none;
  z-index: 10;
  background: linear-gradient(
    to left,
    white,
    transparent
  ); /* Ensure fade-out effect */
}
.answer-option {
  padding-bottom: 2px;
  border-bottom: 2px solid transparent;
}
.selected-answer {
  border-bottom: 2px solid var(--color-cold-purple);
}

/* Carousel dots */
.dot {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background: var(--color-cold-purple-alpha-25);
  border: none;
}
.dot-active {
  background: var(--color-cold-purple);
}

/* Outside navigation buttons */
.important-questions-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  /* remove horizontal padding to avoid causing overflow */
  padding: 0;
}
.card-container {
  position: relative;
  /* Make the card container a consistent width so internal content (number of countries)
     doesn't change the overall component width. It remains centered and responsive. */
  display: block;
  width: 100%;
  /* Use clamp so it naturally shrinks on narrow screens without needing many breakpoints */
  max-width: clamp(300px, 92vw, 820px);
  margin: 0 auto; /* center the card */
}

.card-inner {
  position: relative; /* make nav buttons position relative to the card height */
}
/* Fixed component height */
.card-inner {
  height: 326px;
}

/* Ensure UCard fills the fixed height and internal content scrolls if needed */
.card-container .cold-ucard {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.popular-searches-container {
  flex: 1 1 auto; /* allow inner container to grow and scroll */
  overflow: auto;
}

/* Ensure the UCard fills the container width so the component doesn't shrink/expand
   based on its internal content */
.card-container .cold-ucard {
  width: 100%;
  box-sizing: border-box;
  min-width: 0; /* allow card to shrink within its container and prevent children from forcing expansion */
}
/* Prevent internal flex children from growing the card beyond its max-width */
.countries-lines,
.countries-line {
  max-width: 100%;
  min-width: 0;
}
.country-item {
  white-space: nowrap; /* keep country label and flag on one line */
  display: inline-flex;
  align-items: center;
}
.dots-outside {
  /* ensure dots sit below the card and don't overlap nav buttons */
  margin-top: 12px !important;
  padding-bottom: 0.25rem;
}
.nav-button-outside {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: transparent; /* no circle behind svg */
  border: none;
  padding: 6px; /* keep a comfortable hit area */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  color: var(--color-cold-night);
  transition:
    color 0.15s ease,
    transform 0.12s ease;
  z-index: 20; /* above card */
}
.nav-button-outside:hover {
  /* no hover effect for icons */
  color: var(--color-cold-purple);
  transform: translateY(-50%);
}
.nav-button-outside.left {
  left: -44px;
}
.nav-button-outside.right {
  right: -44px;
}

/* Additional responsive refinements */
@media (max-width: 1024px) {
  .card-inner {
    height: 310px; /* slightly reduce fixed height to create better proportion */
  }
}
@media (max-width: 880px) {
  .nav-button-outside.left {
    left: -32px;
  }
  .nav-button-outside.right {
    right: -32px;
  }
}
@media (max-width: 768px) {
  .important-questions-wrapper {
    padding: 0 1rem; /* tighter side padding */
    overflow-x: hidden; /* prevent any accidental horizontal scroll from nav buttons */
  }
  .card-inner {
    height: 300px; /* keep overall look while allowing a bit more breathing room */
  }
  .nav-button-outside {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }
  .nav-button-outside.left {
    left: -20px; /* reduce negative offset so buttons sit closer to card */
  }
  .nav-button-outside.right {
    right: -20px;
  }
}
@media (max-width: 600px) {
  .nav-button-outside.left {
    left: -12px;
  }
  .nav-button-outside.right {
    right: -12px;
  }
  .card-inner {
    height: 290px;
  }
}
@media (max-width: 480px) {
  .card-inner {
    height: 280px; /* final small reduction; content still scrolls internally if needed */
  }
  .nav-button-outside svg {
    height: 20px;
  }
}
</style>
