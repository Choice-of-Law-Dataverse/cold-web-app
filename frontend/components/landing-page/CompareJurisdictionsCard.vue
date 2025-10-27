<template>
  <UCard class="cold-ucard h-full w-full">
    <h2 class="popular-title">{{ title }}</h2>

    <NuxtLink :to="resolvedButtonLink" class="no-underline">
      <div class="flags-row">
        <div class="flag-cell">
          <img
            v-if="!leftFlagError"
            :src="leftFlagUrl"
            :alt="`${iso3Left} flag`"
            class="flag-img"
            @error="leftFlagError = true"
          >
          <div v-else class="flag-fallback">{{ iso3Left }}</div>
        </div>

        <div class="flag-cell">
          <img
            v-if="!rightFlagError"
            :src="rightFlagUrl"
            :alt="`${rightIso3} flag`"
            class="flag-img"
            @error="rightFlagError = true"
          >
          <div v-else class="flag-fallback">{{ rightIso3 }}</div>
        </div>
      </div>

      <div class="codes-row">
        <div class="code">{{ iso3Left }}</div>
        <div class="code">{{ rightIso3 }}</div>
      </div>
    </NuxtLink>
  </UCard>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";

const props = defineProps({
  title: { type: String, default: "Compare Jurisdictions" },
  buttonText: { type: String, default: "Go to comparison" },
  // Optional: allow overriding the link completely
  buttonLink: { type: String, default: null },
  // ISO3 codes, e.g., 'USA', 'DEU'
  iso3Left: { type: String, required: true },
  iso3Right: { type: String, required: true },
  // If true, the right flag/code will be set to the visitor's country (client-side only)
  detectVisitorRight: { type: Boolean, default: false },
});

const upperLeft = computed(() => (props.iso3Left || "").toUpperCase());
// Right ISO3 can be overridden by visitor detection
const rightIso3 = ref((props.iso3Right || "").toUpperCase());

const leftFlagUrl = computed(
  () =>
    `https://choiceoflaw.blob.core.windows.net/assets/flags/${upperLeft.value.toLowerCase()}.svg`,
);
const rightFlagUrl = computed(
  () =>
    `https://choiceoflaw.blob.core.windows.net/assets/flags/${rightIso3.value.toLowerCase()}.svg`,
);

const leftFlagError = ref(false);
const rightFlagError = ref(false);

const resolvedButtonLink = computed(() => {
  if (props.buttonLink) return props.buttonLink;
  if (!upperLeft.value || !rightIso3.value) return "#";
  return `/jurisdiction-comparison/${upperLeft.value}+${rightIso3.value}`;
});

// Client-side: detect visitor country and set rightIso3
onMounted(async () => {
  if (!props.detectVisitorRight) return;

  // Using Canada as the default fallback for visitor detection
  rightIso3.value = "CAN";
});
</script>

<style scoped>
h2 {
  text-align: center;
}
.flags-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 12px;
  margin-top: 28px;
  margin-bottom: 12px;
}
.flag-cell {
  display: flex;
  justify-content: center;
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
.link-container {
  margin-top: 18px;
  display: flex;
  justify-content: center;
}
</style>
