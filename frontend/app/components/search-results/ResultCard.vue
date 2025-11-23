<template>
  <div class="result-card-container col-span-12">
    <UCard
      v-if="cardType !== 'Loading'"
      class="cold-ucard"
      @click="handleCardClick"
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

      <!-- Card content -->
      <div>
        <slot />
      </div>
    </UCard>
    <UCard v-else class="cold-ucard">
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

<script setup>
import { UCard } from "#components";
import { useRouter } from "vue-router";
import BaseCardHeader from "@/components/ui/BaseCardHeader.vue";

const router = useRouter();

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

function handleCardClick() {
  const link = getCardLink();
  if (link !== "#") {
    router.push(link);
  }
}
</script>

<style scoped>
.result-card-container {
  position: relative;
}

.cold-ucard {
  margin-bottom: 24px;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  cursor: pointer;
}

.cold-ucard:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Trigger arrow bounce animation on card hover */
.cold-ucard:hover :deep(.arrow-icon) {
  animation: bounce-right 0.4s ease-out;
}
</style>
