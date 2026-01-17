<template>
  <NuxtLink :to="buttonLink" class="block h-full">
    <UCard class="cold-ucard number-card h-full">
      <div class="flex h-full flex-col justify-between">
        <h2
          class="card-title mb-4 text-center text-sm font-medium text-gray-600"
        >
          {{ title }}
        </h2>
        <div class="number-container">
          <span v-if="!loading && !error" class="number-display">
            {{ number ?? props.overrideNumber ?? 0 }}
          </span>
          <span v-else-if="loading"><LoadingNumber /></span>
          <span v-else>Error</span>
        </div>
      </div>
    </UCard>
  </NuxtLink>
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
  @apply transition-all duration-200;
}

a:hover .number-card {
  @apply shadow-md;
  transform: translateY(-2px);
}

.card-title {
  line-height: 1.4;
  height: 3.6em;
  display: flex;
  align-items: center;
  justify-content: center;
}

.number-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
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
  font-variant-numeric: tabular-nums;
}

a:hover .number-display {
  filter: brightness(0.85);
}
</style>
