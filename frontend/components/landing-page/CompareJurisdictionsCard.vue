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
      <div class="and-cell">and</div>
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
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}
.flag-cell {
  display: flex;
  justify-content: center;
}
.flag-img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}
.flag-fallback {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  font-weight: 600;
}
.and-cell {
  font-size: 14px;
  color: #6b7280;
}
.codes-row {
  margin-top: 8px;
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
  margin-top: 6px;
  display: flex;
  justify-content: center;
}
@media (min-width: 768px) {
  .flag-img,
  .flag-fallback {
    width: 96px;
    height: 96px;
  }
}
</style>
