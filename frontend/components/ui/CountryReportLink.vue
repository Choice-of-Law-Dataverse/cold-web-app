<template>
  <DetailRow label="Country Report" class="mb-4">
    <NuxtLink
      v-if="countryReportLink"
      :to="countryReportLink"
      class="link-chip--jurisdiction gap-2"
    >
      <img
        v-if="props.jurisdictionCode"
        :src="`https://choiceoflaw.blob.core.windows.net/assets/flags/${props.jurisdictionCode.toLowerCase()}.svg`"
        :alt="`${jurisdictionName} flag`"
        class="h-4 w-4"
      />
      Full questionnaire for {{ jurisdictionName }}
    </NuxtLink>
  </DetailRow>
</template>

<script setup>
import { computed, toRef } from "vue";
import { useRoute } from "vue-router";
import DetailRow from "@/components/ui/DetailRow.vue";
import { useJurisdiction } from "@/composables/useJurisdictions";

const route = useRoute();

const props = defineProps({
  jurisdictionCode: {
    type: String,
    required: true,
  },
});

const jurisdictionCodeRef = toRef(() => props.jurisdictionCode);

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
