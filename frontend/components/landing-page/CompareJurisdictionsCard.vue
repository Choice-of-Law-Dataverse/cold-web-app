<template>
  <UCard class="cold-ucard gradient-top-border h-full w-full">
    <div class="flex flex-col gap-4">
      <div>
        <h2 class="card-title">{{ title }}</h2>
        <p class="card-subtitle">
          Compare legal frameworks across jurisdictions
        </p>
      </div>

      <div v-for="(comparison, index) in comparisons" :key="index">
        <NuxtLink
          :to="`/jurisdiction/${comparison.left}?compare=${comparison.right}#questions-and-answers`"
          class="no-underline"
        >
          <div class="comparison-row">
            <div class="comparison-side">
              <img
                :src="getFlagUrl(comparison.left)"
                :alt="`${comparison.left} flag`"
                class="h-6 w-auto"
              />
              <span class="jurisdiction-code">{{ comparison.left }}</span>
            </div>

            <span class="comparison-vs">vs</span>

            <div class="comparison-side">
              <img
                :src="getFlagUrl(comparison.right)"
                :alt="`${comparison.right} flag`"
                class="h-6 w-auto"
              />
              <span class="jurisdiction-code">{{ comparison.right }}</span>
            </div>
          </div>
        </NuxtLink>
      </div>
    </div>
  </UCard>
</template>

<script setup>
defineProps({
  title: { type: String, default: "Compare Jurisdictions" },
  comparisons: {
    type: Array,
    required: true,
    validator: (value) => value.every((comp) => comp.left && comp.right),
  },
});

const getFlagUrl = (iso3) => {
  return `https://choiceoflaw.blob.core.windows.net/assets/flags/${iso3.toLowerCase()}.svg`;
};
</script>

<style scoped>
.comparison-row {
  @apply flex items-center justify-center gap-6 rounded-lg px-4 py-3 shadow-sm transition-all duration-150;
  background: var(--gradient-subtle);

  &:hover {
    @apply shadow;
    background: var(--gradient-subtle-emphasis);
  }
}

.comparison-side {
  @apply flex w-20 flex-col items-center gap-1;
}

.jurisdiction-code {
  @apply text-sm font-semibold;
  color: var(--color-cold-night);
}

.comparison-vs {
  @apply text-sm font-medium text-gray-400;
}
</style>
