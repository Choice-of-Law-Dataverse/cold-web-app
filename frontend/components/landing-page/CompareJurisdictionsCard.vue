<template>
  <UCard class="cold-ucard h-full w-full">
    <h2 class="popular-title">{{ title }}</h2>

    <div
      v-for="(comparison, index) in comparisons"
      :key="index"
      class="comparison-row"
    >
      <NuxtLink
        :to="`/jurisdiction-comparison/${comparison.left}+${comparison.right}`"
        class="no-underline"
      >
        <div class="flags-row">
          <div class="flag-cell">
            <img
              v-if="!flagErrors[`${index}-left`]"
              :src="getFlagUrl(comparison.left)"
              :alt="`${comparison.left} flag`"
              class="flag-img"
              @error="flagErrors[`${index}-left`] = true"
            >
            <div v-else class="flag-fallback">{{ comparison.left }}</div>
          </div>

          <div class="vs-divider">vs</div>

          <div class="flag-cell">
            <img
              v-if="!flagErrors[`${index}-right`]"
              :src="getFlagUrl(comparison.right)"
              :alt="`${comparison.right} flag`"
              class="flag-img"
              @error="flagErrors[`${index}-right`] = true"
            >
            <div v-else class="flag-fallback">{{ comparison.right }}</div>
          </div>
        </div>

        <div class="codes-row">
          <div class="code">{{ comparison.left }}</div>
          <div class="code">{{ comparison.right }}</div>
        </div>
      </NuxtLink>
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
h2 {
  text-align: center;
}
.comparison-row {
  margin-bottom: 24px;
}
.comparison-row:last-child {
  margin-bottom: 0;
}
.flags-row {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  margin-bottom: 12px;
}
.flag-cell {
  display: flex;
  justify-content: center;
}
.vs-divider {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-cold-gray);
  text-transform: uppercase;
  padding: 0 8px;
}
.flag-img {
  height: 48px;
  width: auto;
  max-width: 100%;
  display: block;
  border: 1px solid var(--color-cold-gray);
}
.flag-fallback {
  height: 36px;
  padding: 0 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border: 1px solid var(--color-cold-gray);
  font-weight: 600;
}

.codes-row {
  margin-top: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.code {
  text-align: center;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.5px;
}
</style>
