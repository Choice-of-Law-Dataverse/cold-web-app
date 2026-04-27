<template>
  <div class="result-card-container col-span-12">
    <a
      v-if="cardType !== 'Loading'"
      :href="cardLink"
      class="card-link-wrapper"
      @click="handleCardClick"
    >
      <UCard
        class="result-card"
        :ui="{
          body: '!p-0',
          header: 'border-b-0 !p-0',
        }"
      >
        <template #header>
          <MetaBand
            v-if="resultData"
            :result-data="resultData"
            :card-type="cardType"
            :formatted-jurisdiction="formattedJurisdiction"
            :formatted-theme="formattedTheme"
            :show-cite="false"
            :show-json="false"
            :show-print="false"
          />
        </template>

        <GradientTopBorder />

        <div class="flex px-6 py-4">
          <slot />
        </div>
      </UCard>
    </a>
    <UCard v-else class="result-card">
      <template #header>
        <USkeleton
          class="mt-0.5 mb-0.5 h-5 w-[100px] rounded-none"
          style="background-color: var(--color-cold-gray-alpha)"
        />
      </template>
      <div>
        <slot />
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { UCard } from "#components";
import MetaBand from "@/components/ui/MetaBand.vue";
import { getBasePathForCard, getEntityConfig } from "@/config/entityRegistry";
import { useEntityDrawer } from "@/composables/useEntityDrawer";
import type { AnySearchResult } from "@/types/search";

const props = withDefaults(
  defineProps<{
    resultData?: AnySearchResult;
    cardType: string;
    formattedTheme?: string[];
    formattedJurisdiction?: string[];
  }>(),
  {
    resultData: () => ({}) as AnySearchResult,
    formattedTheme: () => [],
    formattedJurisdiction: () => [],
  },
);

const { openDrawer } = useEntityDrawer();

const cardLink = computed(() => {
  const basePath = getBasePathForCard(props.cardType);
  if (basePath && props.resultData.id)
    return `${basePath}/${props.resultData.id}`;
  return "#";
});

function handleCardClick(event: MouseEvent) {
  if (event.metaKey || event.ctrlKey) return;
  event.preventDefault();

  const basePath = getBasePathForCard(props.cardType);
  if (!basePath || !props.resultData.id) return;
  const config = getEntityConfig(basePath);
  if (!config) return;

  openDrawer(String(props.resultData.id), config.table, basePath);
}
</script>

<style>
@keyframes bounce-right {
  0% {
    transform: translateX(0);
  }
  40% {
    transform: translateX(8px);
  }
  65% {
    transform: translateX(-2px);
  }
  100% {
    transform: translateX(0);
  }
}
</style>

<style scoped>
.result-card-container {
  position: relative;
}

.card-link-wrapper {
  display: block;
  text-decoration: none;
  color: inherit;
}

.result-card {
  margin-bottom: 24px;
  transition:
    box-shadow 0.2s ease,
    transform 0.2s ease;
  cursor: pointer;
  background: white;
}

.card-link-wrapper:hover .result-card {
  box-shadow:
    0 4px 12px rgba(0, 0, 0, 0.08),
    inset 0 0 0 1px rgba(111, 77, 250, 0.06);
  transform: translateY(-1px);
}

.card-link-wrapper:hover :deep(.icon-action__icon) {
  animation: bounce-right 0.4s ease-out;
}
</style>
