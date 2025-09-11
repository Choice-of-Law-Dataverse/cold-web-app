<template>
  <UCard class="cold-ucard">
    <h2 class="popular-title">{{ title }}</h2>
    <div class="number-container">
      <span v-if="!loading && !error">{{
        number ?? props.overrideNumber ?? 0
      }}</span>
      <span v-else-if="loading"><LoadingNumber /></span>
      <span v-else>Error</span>
    </div>
    <div class="link-container">
      <a :href="buttonLink">
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
import { computed } from 'vue'
import { useNumberCount } from '~/composables/useNumberCount'
import LoadingNumber from '@/components/layout/LoadingNumber.vue'
const props = defineProps({
  title: { type: String, required: true },
  buttonText: { type: String, required: true },
  buttonLink: { type: String, required: true },
  tableName: { type: String, required: true },
  // Optional manual override; when provided, the API will not be called
  overrideNumber: { type: [Number, String], required: false, default: null },
})

// Use the composable for data fetching
const {
  data: number,
  isLoading: loading,
  error,
} = useNumberCount(
  computed(() => (props.overrideNumber ? undefined : props.tableName))
)
</script>

<style scoped>
h2 {
  text-align: center;
}
.number-container {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 90px;
  font-weight: 700;
}
.link-container {
  display: flex;
  justify-content: center;
}
</style>
