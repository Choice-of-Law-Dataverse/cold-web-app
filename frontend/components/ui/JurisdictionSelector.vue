<template>
  <UCard class="cold-ucard overflow-visible">
    <div class="flex flex-col items-stretch gap-8 md:flex-row md:items-center">
      <h3 class="text-left md:whitespace-nowrap">
        Compare
        {{ formattedJurisdiction?.Name || "this jurisdiction" }} with other
        jurisdictions
      </h3>

      <div
        v-if="availableJurisdictions && availableJurisdictions.length > 0"
        class="flex flex-col gap-4 md:flex-row md:items-center"
      >
        <div class="w-full md:w-auto">
          <JurisdictionSelectMenu
            :countries="availableJurisdictions"
            placeholder="Pick a jurisdiction to compare..."
            @country-selected="onJurisdictionSelected"
          />
        </div>
      </div>

      <!-- Loading state -->
      <div v-else-if="isLoading" class="flex items-center gap-2">
        <span class="text-sm text-gray-600">Loading jurisdictions...</span>
      </div>

      <!-- Error/No data state -->
      <div v-else class="flex items-center gap-2">
        <span class="text-sm text-gray-500"
          >Jurisdictions unavailable (API connection required)</span
        >
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";
import { computed } from "vue";
import JurisdictionSelectMenu from "@/components/jurisdiction-comparison/JurisdictionSelectMenu.vue";
import { useJurisdictions } from "@/composables/useJurisdictions";

defineProps({
  formattedJurisdiction: {
    type: Object,
    required: true,
  },
});

const route = useRoute();
const router = useRouter();

const { data: jurisdictions, isLoading } = useJurisdictions();

const currentIso3Code = computed(() => {
  return route.params.id?.toUpperCase();
});

const availableJurisdictions = computed(() => {
  if (!jurisdictions.value || !currentIso3Code.value) return [];

  return jurisdictions.value.filter(
    (jurisdiction) =>
      jurisdiction.alpha3Code?.toUpperCase() !== currentIso3Code.value,
  );
});

const onJurisdictionSelected = (selectedJurisdiction) => {
  if (!selectedJurisdiction?.alpha3Code || !currentIso3Code.value) return;

  const currentCode = currentIso3Code.value.toLowerCase();
  const selectedCode = selectedJurisdiction.alpha3Code.toLowerCase();

  const comparisonUrl = `/jurisdiction-comparison/${currentCode}+${selectedCode}`;
  router.push(comparisonUrl);
};
</script>

<style scoped>
.flex.flex-col.gap-4 {
  position: relative;
  z-index: 10;
}
</style>
