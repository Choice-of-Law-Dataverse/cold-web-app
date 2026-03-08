<template>
  <div class="result-card-container col-span-12">
    <NuxtLink
      v-if="cardType !== 'Loading'"
      :to="getCardLink()"
      class="card-link-wrapper"
    >
      <UCard
        class="result-card"
        :ui="{
          body: '!p-0',
          header: 'border-b-0 px-6 py-5',
        }"
      >
        <template #header>
          <BaseCardHeader
            v-if="resultData"
            :result-data="resultData"
            :card-type="cardType"
            :show-open-link="true"
            :formatted-jurisdiction="formattedJurisdiction"
            :formatted-theme="formattedTheme"
            :show-suggest-edit="false"
          />
        </template>

        <!-- Gradient divider between header and content -->
        <div class="gradient-top-border" />

        <div class="flex px-6 py-5">
          <slot />
        </div>
      </UCard>
    </NuxtLink>
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
import { UCard } from "#components";
import BaseCardHeader from "@/components/ui/CardHeader.vue";

const props = withDefaults(
  defineProps<{
    resultData?: Record<string, unknown>;
    cardType: string;
    formattedTheme?: string[];
    formattedJurisdiction?: string[];
  }>(),
  {
    resultData: () => ({}),
    formattedTheme: () => [],
    formattedJurisdiction: () => [],
  },
);

function getCardLink() {
  switch (props.cardType) {
    case "Answers":
      return `/question/${props.resultData.id}`;
    case "Court Decisions":
      return `/court-decision/${props.resultData.id}`;
    case "Domestic Instrument":
      return `/domestic-instrument/${props.resultData.id}`;
    case "Regional Instrument":
      return `/regional-instrument/${props.resultData.id}`;
    case "International Instrument":
      return `/international-instrument/${props.resultData.id}`;
    case "Arbitral Rule":
    case "Arbitral Rules":
      return `/arbitral-rule/${props.resultData.id}`;
    case "Arbitral Award":
    case "Arbitral Awards":
      return `/arbitral-award/${props.resultData.id}`;
    case "Literature":
      return `/literature/${props.resultData.id}`;
    default:
      return "#";
  }
}
</script>

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
  transition: box-shadow 0.2s ease;
  cursor: pointer;
}

.card-link-wrapper:hover .result-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Trigger arrow bounce animation on card hover */
.card-link-wrapper:hover :deep(.arrow-icon) {
  animation: bounce-right 0.4s ease-out;
}
</style>
