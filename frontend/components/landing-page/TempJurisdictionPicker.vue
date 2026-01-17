<template>
  <UCard class="cold-ucard overflow-visible">
    <div class="flex flex-col gap-6 md:flex-row md:items-center">
      <h2 class="card-title whitespace-nowrap">Open a Country Report</h2>
      <div class="suggestions w-full">
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

const navigateToCountry = async (country) =>
  router.push(`/jurisdiction/${country.alpha3Code.toLowerCase()}`);
</script>

<style scoped>
.suggestions {
  display: flex;
  flex-wrap: wrap;
  position: relative;
}
</style>
