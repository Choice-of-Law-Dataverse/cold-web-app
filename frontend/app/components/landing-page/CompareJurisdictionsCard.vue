<template>
  <UCard
    class="cold-ucard h-full w-full overflow-hidden"
    :ui="{ body: '!p-0' }"
  >
    <div class="gradient-top-border" />
    <div class="flex flex-col gap-4 p-4 sm:p-6">
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
              <JurisdictionFlag
                :iso3="comparison.left"
                size="lg"
                :alt="`${comparison.left} flag`"
              />
              <span class="jurisdiction-code">{{ comparison.left }}</span>
            </div>

            <span class="comparison-vs">vs</span>

            <div class="comparison-side">
              <JurisdictionFlag
                :iso3="comparison.right"
                size="lg"
                :alt="`${comparison.right} flag`"
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
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";

defineProps({
  title: { type: String, default: "Compare Jurisdictions" },
  comparisons: {
    type: Array,
    required: true,
    validator: (value) => value.every((comp) => comp.left && comp.right),
  },
});
</script>

<style scoped>
@reference "tailwindcss";

.comparison-row {
  @apply flex items-center justify-center gap-6 rounded-lg px-4 py-3 shadow-sm transition-all duration-150;
  background: var(--gradient-subtle);
}

.comparison-row:hover {
  @apply shadow;
  background: var(--gradient-subtle-emphasis);
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
