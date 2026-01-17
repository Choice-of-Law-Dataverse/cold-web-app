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
          <div
            class="comparison-row hover-row flex items-start justify-between p-2"
          >
            <div
              class="comparison-side flex min-w-[100px] flex-col items-center gap-2"
            >
              <div
                class="flag-container flex h-12 w-full items-center justify-center"
              >
                <img
                  v-if="!flagErrors[`${index}-left`]"
                  :src="getFlagUrl(comparison.left)"
                  :alt="`${comparison.left} flag`"
                  class="comparison-flag block h-12 w-auto max-w-full"
                  @error="flagErrors[`${index}-left`] = true"
                />
                <div
                  v-else
                  class="flag-fallback inline-flex h-9 items-center justify-center border border-gray-300 bg-gray-100 px-3 font-semibold"
                >
                  {{ comparison.left }}
                </div>
              </div>
              <div
                class="jurisdiction-name text-center text-sm font-semibold tracking-wider text-[var(--color-cold-night)]"
              >
                {{ comparison.left }}
              </div>
            </div>

            <div
              class="comparison-vs mt-3 self-center px-2 text-sm font-semibold uppercase text-gray-400"
            >
              vs
            </div>

            <div
              class="comparison-side flex min-w-[100px] flex-col items-center gap-2 md:min-w-[120px]"
            >
              <div
                class="flag-container flex h-12 w-full items-center justify-center"
              >
                <img
                  v-if="!flagErrors[`${index}-right`]"
                  :src="getFlagUrl(comparison.right)"
                  :alt="`${comparison.right} flag`"
                  class="comparison-flag block h-12 w-auto max-w-full"
                  @error="flagErrors[`${index}-right`] = true"
                />
                <div
                  v-else
                  class="flag-fallback inline-flex h-9 items-center justify-center border border-gray-300 bg-gray-100 px-3 font-semibold"
                >
                  {{ comparison.right }}
                </div>
              </div>
              <div
                class="jurisdiction-name text-center text-sm font-semibold tracking-wider text-[var(--color-cold-night)]"
              >
                {{ comparison.right }}
              </div>
            </div>
          </div>
        </NuxtLink>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { ref } from "vue";

defineProps({
  title: { type: String, default: "Compare Jurisdictions" },
  comparisons: {
    type: Array,
    required: true,
    validator: (value) => value.every((comp) => comp.left && comp.right),
  },
});

const flagErrors = ref({});

const getFlagUrl = (iso3) => {
  return `https://choiceoflaw.blob.core.windows.net/assets/flags/${iso3.toLowerCase()}.svg`;
};
</script>

<style scoped>
.comparison-row {
  @apply p-2 shadow-sm;
}

.comparison-flag {
  @apply rounded border border-gray-200;
}

.comparison-vs {
  @apply relative text-gray-400 transition-colors duration-200;
}

.comparison-row:hover .comparison-vs {
  color: var(--color-cold-green);
}

.jurisdiction-name {
  @apply text-center text-sm font-semibold uppercase tracking-wider transition-colors duration-200;
  color: var(--color-cold-night);
}

.comparison-row:hover .jurisdiction-name {
  color: var(--color-cold-purple);
}

.flag-fallback {
  @apply inline-flex h-9 items-center justify-center border border-gray-300 bg-gray-100 px-3 font-semibold;
}
</style>
