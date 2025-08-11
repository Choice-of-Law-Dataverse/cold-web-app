<template>
  <UCard class="cold-ucard">
    <div class="popular-searches-container flex flex-col gap-8">
      <div>
        <h2 class="popular-title text-left">
          Is there a codification on choice of law?
        </h2>
        <div>
          <h3 class="mt-4">
            <span v-for="(option, idx) in answers" :key="option" class="mr-4">
              {{ option }}
            </span>
          </h3>
        </div>

        <div>
          <p class="label mt-4 regions-scroll">
            <span v-for="(region, idx) in regions" :key="region" class="mr-4">
              {{ region }}
            </span>
          </p>
        </div>
      </div>
    </div>
  </UCard>
</template>

<script setup>
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
</style>
