<template>
  <UCard class="cold-ucard">
    <h2 class="popular-title">{{ title }}</h2>

    <div class="flags-row">
      <div class="flag-cell">
        <img
          v-if="!leftFlagError"
          :src="leftFlagUrl"
          :alt="`${iso3Left} flag`"
          class="flag-img"
          @error="leftFlagError = true"
        />
        <div v-else class="flag-fallback">{{ iso3Left }}</div>
      </div>

      <div class="flag-cell">
        <img
          v-if="!rightFlagError"
          :src="rightFlagUrl"
          :alt="`${iso3Right} flag`"
          class="flag-img"
          @error="rightFlagError = true"
        />
        <div v-else class="flag-fallback">{{ iso3Right }}</div>
      </div>
    </div>

    <div class="codes-row">
      <div class="code">{{ iso3Left }}</div>
      <div class="code">{{ iso3Right }}</div>
    </div>

    <div class="link-container">
      <a :href="resolvedButtonLink">
        <UButton
          class="suggestion-button"
          variant="link"
          icon="i-material-symbols:arrow-forward"
          trailing
        >
          {{ buttonText }}
        </UButton>
      </a>
    </div>
  </UCard>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  title: { type: String, default: 'Compare Jurisdictions' },
  buttonText: { type: String, default: 'Go to comparison' },
  // Optional: allow overriding the link completely
  buttonLink: { type: String, default: null },
  // ISO3 codes, e.g., 'USA', 'DEU'
  iso3Left: { type: String, required: true },
  iso3Right: { type: String, required: true },
})

const upperLeft = computed(() => (props.iso3Left || '').toUpperCase())
const upperRight = computed(() => (props.iso3Right || '').toUpperCase())

const leftFlagUrl = computed(
  () =>
    `https://choiceoflaw.blob.core.windows.net/assets/flags/${upperLeft.value.toLowerCase()}.svg`
)
const rightFlagUrl = computed(
  () =>
    `https://choiceoflaw.blob.core.windows.net/assets/flags/${upperRight.value.toLowerCase()}.svg`
)

const leftFlagError = ref(false)
const rightFlagError = ref(false)

const resolvedButtonLink = computed(() => {
  if (props.buttonLink) return props.buttonLink
  if (!upperLeft.value || !upperRight.value) return '#'
  return `/jurisdiction-comparison/${upperLeft.value}+${upperRight.value}`
})
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
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.link-container {
  margin-top: 18px;
  display: flex;
  justify-content: center;
}
</style>
