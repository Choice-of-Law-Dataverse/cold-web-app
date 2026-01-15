<template>
  <UCard class="cold-ucard number-card h-full">
    <div class="flex h-full flex-col justify-between">
      <h2 class="card-title mb-4 text-center text-sm font-medium text-gray-600">
        {{ title }}
      </h2>
      <div class="number-container">
        <span v-if="!loading && !error">
          <NuxtLink :to="buttonLink">
            <div class="number-display group">
              {{ number ?? props.overrideNumber ?? 0 }}
            </div>
          </NuxtLink>
        </span>
        <span v-else-if="loading"><LoadingNumber /></span>
        <span v-else>Error</span>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { computed } from "vue";
import { useNumberCount } from "~/composables/useNumberCount";
import LoadingNumber from "@/components/layout/LoadingNumber.vue";
const props = defineProps({
  title: { type: String, required: true },
  buttonText: { type: String, required: true },
  buttonLink: { type: String, required: true },
  tableName: { type: String, required: true },
  overrideNumber: { type: [Number, String], required: false, default: null },
});

const {
  data: number,
  isLoading: loading,
  error,
} = useNumberCount(
  computed(() => (props.overrideNumber ? undefined : props.tableName)),
);
</script>

<style scoped>
.number-card {
  @apply transition-shadow duration-200;
}

.number-card:hover {
  @apply shadow-md;
}

.card-title {
  line-height: 1.4;
}

.number-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100px;
  flex: 1;
}

.number-display {
  font-size: 64px;
  font-weight: 700;
  background: linear-gradient(
    135deg,
    var(--color-cold-purple),
    var(--color-cold-green)
  );
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  cursor: pointer;
  transition: filter 0.2s ease;
}

.number-display:hover {
  filter: brightness(0.85);
}
</style>
