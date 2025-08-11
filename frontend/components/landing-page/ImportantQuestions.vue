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
              <span v-for="(region, idx) in regions" :key="region" class="mr-4">
                {{ region }}
              </span>
            </p>
          </div>
          <div
            v-if="selectedAnswer && countries.length"
            class="countries-scroll mt-2"
          >
            <span
              v-for="country in countries"
              :key="country"
              class="country-item"
            >
              {{ country }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { ref } from 'vue'
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

const selectedAnswer = ref('')
const countries = ref([])
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
    countries.value = data
      .filter((item) => item['Jurisdictions Irrelevant'] !== 'True')
      .map((item) => item.Jurisdictions)
      .sort((a, b) => a.localeCompare(b))
  } catch (e) {
    countries.value = ['Error loading countries']
  }
}

function selectAnswer(answer) {
  selectedAnswer.value = answer
  fetchCountries()
}
</script>

<style scoped>
.label {
  font-weight: 600 !important;
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
  display: flex;
  flex-wrap: wrap;
  max-height: calc(3 * 2.2em); /* 3 lines, adjust line height as needed */
  overflow-x: auto;
  overflow-y: hidden;
  gap: 1em;
  align-items: flex-start;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.countries-scroll::-webkit-scrollbar {
  display: none;
}
.country-item {
  white-space: nowrap;
}
</style>
