<template>
  <UCard class="cold-ucard">
    <div class="popular-searches-container flex flex-col gap-8">
      <div>
        <h2 class="popular-title text-left">
          Is there a codification on choice of law?
        </h2>
        <div>
          <h3 class="mt-4">
            <span
              v-for="(option, idx) in answers"
              :key="option"
              class="mr-4 cursor-pointer"
              @click="selectAnswer(option)"
              :style="{
                fontWeight: selectedAnswer === option ? 'bold' : 'normal',
              }"
            >
              {{ option }}
            </span>
          </h3>
          <div>
            <p class="label mt-4 mb-4 regions-scroll">
              <span
                v-for="(region, idx) in regions"
                :key="region"
                class="mr-4 region-label"
                :style="{
                  color: selectedRegion === region ? '#2563eb' : '',
                  cursor: 'pointer',
                  fontWeight: selectedRegion === region ? 'bold' : 'normal',
                }"
                @click="selectRegion(region)"
              >
                {{ region }}
              </span>
            </p>
          </div>
          <div
            v-if="selectedAnswer && countriesLines.length"
            class="countries-scroll mt-2"
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
                  class="country-item label-jurisdiction"
                  :href="`/question/${country.code}_01-P`"
                  >{{ country.name }}</a
                >
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { ref, onMounted } from 'vue'
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
        filters: [
          {
            column: 'Question',
            value: 'Is there a codification on choice of law?',
          },
          { column: 'Answer', value: selectedAnswer.value },
        ],
      }),
    })
    if (!res.ok) throw new Error('API error')
    const data = await res.json()
    let filtered = data.filter(
      (item) => item['Jurisdictions Irrelevant'] !== 'True'
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
  overflow-x: auto;
  overflow-y: hidden;
  max-height: 6.6em; /* 3 lines * 2.2em */
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.countries-scroll::-webkit-scrollbar {
  display: none;
}
.countries-lines {
  display: inline-flex;
  flex-direction: column;
  gap: 0.5em;
}
.countries-line {
  display: inline-flex;
  gap: 1em;
}
.country-item {
  display: inline-block;
  margin-right: 0em !important;
  margin-bottom: 0.5em;
  white-space: nowrap;
}
.region-label {
  transition:
    color 0.2s,
    font-weight 0.2s;
}
</style>
