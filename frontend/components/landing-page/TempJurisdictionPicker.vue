<template>
  <UCard class="cold-ucard overflow-visible">
    <div class="flex flex-col gap-6 md:flex-row md:items-center">
      <h2 class="popular-title">Open a Country Report</h2>
      <div class="suggestions w-full md:w-auto">
        <JurisdictionSelectMenu
          :countries="jurisdictions || []"
          @country-selected="navigateToCountry"
        />
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { useRouter } from "vue-router";
import JurisdictionSelectMenu from "@/components/jurisdiction-comparison/JurisdictionSelectMenu.vue";
import { useJurisdictions } from "@/composables/useJurisdictions";

const router = useRouter();

const { data: jurisdictions } = useJurisdictions();

// Navigate to country route
const navigateToCountry = async (country) =>
  router.push(`/jurisdiction/${country.alpha3Code.toLowerCase()}`);
</script>

<style scoped>
.popular-title {
  white-space: nowrap; /* Prevents title from wrapping */
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  position: relative; /* Additional positioning context for the dropdown */
}
</style>
