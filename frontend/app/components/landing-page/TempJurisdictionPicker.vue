<template>
  <UCard :ui="{ root: 'overflow-visible' }">
    <div class="flex flex-col gap-6 md:flex-row md:items-center">
      <h2 class="card-title whitespace-nowrap">Open a Jurisdiction Report</h2>
      <div v-if="isLoading" class="suggestions w-full">
        <USkeleton class="h-10 w-full" />
      </div>
      <InlineError v-else-if="error" :error="error" />
      <div v-else class="suggestions w-full">
        <JurisdictionSelectMenu
          :jurisdictions="jurisdictions || []"
          @jurisdiction-selected="navigateToJurisdiction"
        />
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import JurisdictionSelectMenu from "@/components/jurisdiction/JurisdictionSelectMenu.vue";
import InlineError from "@/components/ui/InlineError.vue";
import { useJurisdictions } from "@/composables/useJurisdictions";
import type { JurisdictionOption } from "@/types/analyzer";

const router = useRouter();

const { data: jurisdictions, isLoading, error } = useJurisdictions();

const navigateToJurisdiction = async (
  jurisdiction: JurisdictionOption | undefined,
) => {
  if (jurisdiction?.alpha3Code) {
    await router.push(`/jurisdiction/${jurisdiction.alpha3Code.toLowerCase()}`);
  }
};
</script>

<style scoped>
.suggestions {
  display: flex;
  flex-wrap: wrap;
  position: relative;
}
</style>
