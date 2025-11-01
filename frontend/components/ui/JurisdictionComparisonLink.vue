<template>
  <UCard class="cold-ucard">
    <div class="flex flex-col gap-8">
      <div>
        <h3 class="text-left md:whitespace-nowrap">
          <NuxtLink
            v-if="formattedJurisdiction?.Name && iso3Code"
            :to="comparisonUrl"
          >
            Compare
            {{ formattedJurisdiction?.Name || "this jurisdiction" }} with other
            jurisdictions
          </NuxtLink>
          <span v-else>
            Compare
            {{ formattedJurisdiction?.Name || "this jurisdiction" }} with other
            jurisdictions
          </span>
        </h3>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { useRoute } from "vue-router";
import { computed } from "vue";

defineProps({
  formattedJurisdiction: {
    type: Object,
    required: true,
  },
});

const route = useRoute();

const iso3Code = computed(() => {
  return route.params.id?.toUpperCase();
});

const secondJurisdictionCode = computed(() => {
  const current = iso3Code.value?.toLowerCase();
  return current === "ago" ? "arg" : "ago";
});

const comparisonUrl = computed(() => {
  if (!iso3Code.value) return "#";

  const codes = [iso3Code.value.toLowerCase(), secondJurisdictionCode.value];

  return `/jurisdiction-comparison/${codes.join("+")}`;
});
</script>

<style scoped>
h3 {
  color: var(--color-cold-purple) !important;
}
</style>
