<template>
  <NuxtLink
    v-if="jurisdictionCode && countryReportLink"
    :to="countryReportLink"
    class="group from-cold-purple/5 via-cold-teal/5 to-cold-purple/5 hover:from-cold-purple/10 hover:via-cold-teal/10 hover:to-cold-purple/10 relative block overflow-hidden rounded-b-lg bg-gradient-to-r px-6 py-5 transition-all duration-300 sm:px-8"
  >
    <!-- Subtle animated gradient overlay -->
    <div
      class="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100"
      style="animation: shimmer 2s infinite; background-size: 200% 100%"
    />

    <div class="relative flex items-center justify-between">
      <!-- Text content -->
      <div class="flex items-center gap-3">
        <div
          class="bg-cold-purple/15 group-hover:bg-cold-purple/25 flex h-8 w-8 items-center justify-center rounded-full transition-all duration-300 group-hover:scale-110"
        >
          <UIcon
            name="i-heroicons-document-text"
            class="text-cold-purple h-4 w-4"
          />
        </div>
        <div class="flex flex-col">
          <span
            class="text-cold-purple text-xs font-semibold tracking-wide uppercase"
          >
            Country Report
          </span>
          <span
            class="group-hover:text-cold-purple text-sm font-semibold text-gray-700 transition-colors duration-300"
          >
            Full questionnaire for {{ jurisdictionName }}
          </span>
        </div>
      </div>

      <!-- Flag and arrow -->
      <div class="flex items-center gap-4">
        <JurisdictionFlag
          v-if="jurisdictionCode"
          :iso3="jurisdictionCode"
          size="lg"
          :alt="`${jurisdictionName} flag`"
          class="transition-transform duration-300 group-hover:scale-105"
        />
        <div
          class="bg-cold-purple/10 group-hover:bg-cold-purple flex h-8 w-8 items-center justify-center rounded-full transition-all duration-300 group-hover:translate-x-1 group-hover:shadow-lg"
        >
          <UIcon
            name="i-heroicons-arrow-right-20-solid"
            class="text-cold-purple h-4 w-4 transition-colors duration-300 group-hover:text-white"
          />
        </div>
      </div>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
import { computed, toRef } from "vue";
import { useRoute } from "vue-router";
import { useJurisdiction } from "@/composables/useJurisdictions";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";

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

<style scoped>
@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
</style>
