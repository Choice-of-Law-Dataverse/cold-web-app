<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <UCard class="cold-ucard overflow-visible">
          <div
            class="flex flex-col items-stretch gap-8 md:flex-row md:items-center"
          >
            <h3 class="text-left md:whitespace-nowrap">
              Compare
              {{ formattedJurisdiction?.Name || "this jurisdiction" }} with
              other jurisdictions
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
              <span class="text-sm text-gray-600"
                >Loading jurisdictions...</span
              >
            </div>

            <!-- Error/No data state -->
            <div v-else class="flex items-center gap-2">
              <span class="text-sm text-gray-500"
                >Jurisdictions unavailable (API connection required)</span
              >
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </main>
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";
import { computed } from "vue";
import JurisdictionSelectMenu from "@/components/jurisdiction-comparison/JurisdictionSelectMenu.vue";
import { useJurisdictions } from "@/composables/useJurisdictions";

// Accept processedAnswerData as a prop from parent
defineProps({
  formattedJurisdiction: {
    type: Object,
    required: true,
  },
});

const route = useRoute();
const router = useRouter();

// Get all jurisdictions for the selector
const { data: jurisdictions, isLoading } = useJurisdictions();

// Get the current ISO3 code from the route params
const currentIso3Code = computed(() => {
  return route.params.id?.toUpperCase();
});

// Filter out the current jurisdiction from available options
const availableJurisdictions = computed(() => {
  if (!jurisdictions.value || !currentIso3Code.value) return [];

  return jurisdictions.value.filter(
    (jurisdiction) =>
      jurisdiction.alpha3Code?.toUpperCase() !== currentIso3Code.value,
  );
});

// Handle jurisdiction selection and navigate to comparison page
const onJurisdictionSelected = (selectedJurisdiction) => {
  if (!selectedJurisdiction?.alpha3Code || !currentIso3Code.value) return;

  const currentCode = currentIso3Code.value.toLowerCase();
  const selectedCode = selectedJurisdiction.alpha3Code.toLowerCase();

  // Navigate to comparison page with format: current+selected
  const comparisonUrl = `/jurisdiction-comparison/${currentCode}+${selectedCode}`;
  router.push(comparisonUrl);
};
</script>

<style scoped>
h3 {
  color: var(--color-cold-purple) !important;
}

/* Ensure proper positioning context for the dropdown */
.flex.flex-col.gap-4 {
  position: relative;
  z-index: 10;
}
</style>
