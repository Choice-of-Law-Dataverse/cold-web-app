<template>
  <UCard class="cold-ucard h-full w-full">
    <div class="flex flex-col gap-4">
      <div>
        <h2 class="popular-title">{{ title }}</h2>
        <p class="result-value-small">
          Compare legal frameworks across jurisdictions
        </p>
      </div>

      <div v-for="(comparison, index) in comparisons" :key="index">
        <NuxtLink
          :to="`/jurisdiction/${comparison.left}?compare=${comparison.right}#questions-and-answers`"
          class="no-underline"
        >
          <div
            class="flex items-start justify-between rounded-lg p-1 transition-colors duration-200 hover:bg-gray-50"
          >
            <div class="flex min-w-[100px] flex-col items-center gap-2">
              <div class="flex h-12 w-full items-center justify-center">
                <img
                  v-if="!flagErrors[`${index}-left`]"
                  :src="getFlagUrl(comparison.left)"
                  :alt="`${comparison.left} flag`"
                  class="block h-12 w-auto max-w-full border border-[var(--color-cold-gray)]"
                  @error="flagErrors[`${index}-left`] = true"
                />
                <div
                  v-else
                  class="inline-flex h-9 items-center justify-center border border-[var(--color-cold-gray)] bg-gray-100 px-3 font-semibold"
                >
                  {{ comparison.left }}
                </div>
              </div>
              <div
                class="text-center text-sm font-semibold tracking-wider text-[var(--color-cold-night)]"
              >
                {{ comparison.left }}
              </div>
            </div>

            <div
              class="mt-3 self-center px-2 text-sm font-semibold uppercase text-[var(--color-cold-gray)]"
            >
              vs
            </div>

            <div
              class="flex min-w-[100px] flex-col items-center gap-2 md:min-w-[120px]"
            >
              <div class="flex h-12 w-full items-center justify-center">
                <img
                  v-if="!flagErrors[`${index}-right`]"
                  :src="getFlagUrl(comparison.right)"
                  :alt="`${comparison.right} flag`"
                  class="block h-12 w-auto max-w-full border border-[var(--color-cold-gray)]"
                  @error="flagErrors[`${index}-right`] = true"
                />
                <div
                  v-else
                  class="inline-flex h-9 items-center justify-center border border-[var(--color-cold-gray)] bg-gray-100 px-3 font-semibold"
                >
                  {{ comparison.right }}
                </div>
              </div>
              <div
                class="text-center text-sm font-semibold tracking-wider text-[var(--color-cold-night)]"
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
