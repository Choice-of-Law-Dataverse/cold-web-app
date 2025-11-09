<template>
  <UCard class="cold-ucard">
    <div class="flex flex-col gap-8">
      <!-- Title Section -->
      <div>
        <h3 class="mb-1 text-left md:whitespace-nowrap">
          <NuxtLink v-if="jurisdictionCode" :to="countryReportLink">
            Country report for
            {{ processedAnswerData?.Jurisdictions || "this jurisdiction" }}
          </NuxtLink>
          <span v-else>
            Country report for
            {{ processedAnswerData?.Jurisdictions || "this jurisdiction" }}
          </span>
        </h3>
        <span class="result-value-small">
          The country report provides detailed information, answers, and more on
          {{ processedAnswerData?.Jurisdictions || "this jurisdiction" }}
        </span>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const props = defineProps({
  processedAnswerData: {
    type: Object,
    required: false,
    default: () => ({}),
  },
});

const jurisdictionCode = computed(() => {
  return (
    props.processedAnswerData?.["Jurisdictions Alpha-3 code"] ||
    props.processedAnswerData?.["Jurisdictions Alpha-3 Code"]
  );
});

const questionId = computed(() => {
  // Extract question ID from the answer ID (route param)
  // Answer ID format: {ISO3_CODE}_{QUESTION_ID}
  const answerId = route.params.id as string;
  if (!answerId) return null;

  const parts = answerId.split('_');
  if (parts.length > 1) {
    // Return everything after the first underscore
    return parts.slice(1).join('_');
  }
  return null;
});

const countryReportLink = computed(() => {
  const baseLink = `/jurisdiction/${jurisdictionCode.value?.toLowerCase()}`;
  if (questionId.value) {
    return `${baseLink}#question-${questionId.value}`;
  }
  return baseLink;
});
</script>

<style scoped>
h3 {
  color: var(--color-cold-purple) !important;
}
</style>
