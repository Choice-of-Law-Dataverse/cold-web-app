<template>
  <UCard class="cold-ucard h-full">
    <h2 class="popular-title">{{ title }}</h2>
    <div class="number-container">
      <span v-if="!loading && !error">
        <NuxtLink :to="buttonLink">
          <UButton class="suggestion-button" variant="link" trailing>{{
            number ?? props.overrideNumber ?? 0
          }}</UButton>
        </NuxtLink>
      </span>
      <span v-else-if="loading"><LoadingNumber /></span>
      <span v-else>Error</span>
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
h2 {
  text-align: center;
}
.number-container {
  display: flex;
  justify-content: center;
  align-items: center;
}
.number-container button {
  font-size: 72px !important;
  font-weight: 700 !important;
}
</style>
