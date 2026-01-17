<template>
  <div
    v-if="jurisdictionCode && countryReportLink"
    class="border-t border-gray-100 bg-gray-50/50 px-6 py-4 sm:px-8"
  >
    <NuxtLink :to="countryReportLink" class="group flex items-center gap-3">
      <img
        v-if="jurisdictionCode"
        :src="`https://choiceoflaw.blob.core.windows.net/assets/flags/${jurisdictionCode.toLowerCase()}.svg`"
        :alt="`${jurisdictionName} flag`"
        class="h-5 w-5 rounded-sm shadow-sm"
      />
      <span
        class="text-sm font-medium text-cold-gray-dark transition-colors group-hover:text-cold-purple"
      >
        Full questionnaire for {{ jurisdictionName }}
      </span>
      <UIcon
        name="i-heroicons-arrow-right-20-solid"
        class="h-4 w-4 text-cold-gray transition-transform group-hover:translate-x-0.5 group-hover:text-cold-purple"
      />
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
import { computed, toRef } from "vue";
import { useRoute } from "vue-router";
import { useJurisdiction } from "@/composables/useJurisdictions";

const route = useRoute();

const props = defineProps<{
  jurisdictionCode?: string;
}>();

const jurisdictionCodeRef = toRef(() => props.jurisdictionCode || "");

const { data: jurisdiction } = useJurisdiction(jurisdictionCodeRef);

const jurisdictionName = computed(() => {
  return jurisdiction.value?.Name || "this jurisdiction";
});

const questionId = computed(() => {
  // Extract question ID from the answer ID (route param)
  // Answer ID format: {ISO3_CODE}_{QUESTION_ID}
  const answerId = route.params.id;
  if (!answerId || typeof answerId !== "string") return null;

  const parts = answerId.split("_");
  if (parts.length > 1) {
    // Return everything after the first underscore
    return parts.slice(1).join("_");
  }
  return null;
});

const countryReportLink = computed(() => {
  if (!props.jurisdictionCode) return null;
  const baseLink = `/jurisdiction/${props.jurisdictionCode.toLowerCase()}`;
  if (questionId.value) {
    return `${baseLink}#question-${questionId.value}`;
  }
  return baseLink;
});
</script>
