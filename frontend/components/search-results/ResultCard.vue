<template>
  <div class="result-card-container col-span-12">
    <NuxtLink
      v-if="cardType !== 'Loading'"
      :to="getCardLink()"
      class="card-link-wrapper"
    >
      <UCard
        class="cold-ucard"
        :ui="{
          base: 'overflow-hidden',
          body: {
            base: 'flex gradient-top-border',
            padding: 'px-6 py-5',
          },
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

        <slot />
      </UCard>
    </NuxtLink>
    <UCard v-else class="cold-ucard">
      <template #header>
        <USkeleton
          class="mb-0.5 mt-0.5 h-5 w-[100px] rounded-none"
          style="background-color: var(--color-cold-gray-alpha)"
        />
      </template>
      <div>
        <slot />
      </div>
    </UCard>
  </div>
</template>

<script setup>
import { UCard } from "#components";
import BaseCardHeader from "@/components/ui/BaseCardHeader.vue";

const props = defineProps({
  resultData: {
    type: Object,
    required: false,
    default: () => ({}),
  },
  cardType: {
    type: String,
    required: true,
  },
  formattedTheme: {
    type: Array,
    required: false,
    default: () => [],
  },
  formattedJurisdiction: {
    type: Array,
    required: false,
    default: () => [],
  },
});

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
      return `/arbitral-rule/${props.resultData.id}`;
    case "Arbitral Award":
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

.cold-ucard {
  margin-bottom: 24px;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  cursor: pointer;
}

.card-link-wrapper:hover .cold-ucard {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Trigger arrow bounce animation on card hover */
.card-link-wrapper:hover :deep(.arrow-icon) {
  animation: bounce-right 0.4s ease-out;
}
</style>
