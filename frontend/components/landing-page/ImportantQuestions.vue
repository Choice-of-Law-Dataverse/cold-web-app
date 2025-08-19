<template>
  <div class="important-questions-wrapper relative">
    <div class="card-container">
      <button
        class="nav-button-outside left"
        aria-label="Previous question"
        @click="prevQuestion"
        type="button"
      >
        ◀
      </button>
      <UCard class="cold-ucard">
        <div class="popular-searches-container flex flex-col gap-8">
          <div>
            <div class="flex items-center justify-center md:justify-between">
              <h2 class="popular-title text-center md:text-left mb-0">
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
                <p class="label mt-6 mb-6 regions-scroll">
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
                          :src="`https://choiceoflawdataverse.blob.core.windows.net/assets/flags/${country.code?.toLowerCase()}.svg`"
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
                </div>
                <div v-else class="mt-4 copy">
                  No jurisdictions to be displayed
                </div>
              </div>
            </div>
            <!-- Dots navigation -->
            <div class="mt-4">
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
      </UCard>
      <button
        class="nav-button-outside right"
        aria-label="Next question"
        @click="nextQuestion"
        type="button"
      >
        ▶
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
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
    const res = await fetch(`${config.public.apiBaseUrl}/search/full_table`, {
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

    // Populate questionTitle from API response (use first matching row)
    if (
      dataWithSuffix.length > 0 &&
      typeof dataWithSuffix[0].Question === 'string'
    ) {
      questionTitle.value = dataWithSuffix[0].Question
    }

    let filtered = dataWithSuffix.filter(
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
    countriesLines.value = splitIntoThreeLines(list)
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
})

function splitIntoThreeLines(items) {
  // Split already-sorted items into 3 contiguous rows with equal counts when possible.
  // Any remainder (n % 3) is distributed to the first rows to keep them balanced.
  const n = items.length
  const base = Math.floor(n / 3)
  const rem = n % 3 // 0,1,2

  const size1 = base + (rem > 0 ? 1 : 0)
  const size2 = base + (rem > 1 ? 1 : 0)
  const size3 = n - size1 - size2

  const firstEnd = size1
  const secondEnd = size1 + size2

  return [
    items.slice(0, firstEnd),
    items.slice(firstEnd, secondEnd),
    items.slice(secondEnd),
  ]
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
  width: 10px;
  height: 10px;
  border-radius: 9999px;
  background: #d1d5db; /* gray-300 */
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
  display: inline-block; /* shrink-wrap to card width */
}
.nav-button-outside {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: #ffffff;
  border: 1px solid #e5e7eb; /* gray-200 */
  border-radius: 9999px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  transition:
    background 0.15s ease,
    color 0.15s ease,
    box-shadow 0.15s ease;
  z-index: 20; /* above card */
}
.nav-button-outside:hover {
  background: var(--color-cold-purple);
  color: #fff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
}
.nav-button-outside.left {
  left: -44px;
}
.nav-button-outside.right {
  right: -44px;
}

@media (max-width: 768px) {
  .important-questions-wrapper {
    padding: 0 1.5rem;
  }
  .nav-button-outside {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }
}
</style>
