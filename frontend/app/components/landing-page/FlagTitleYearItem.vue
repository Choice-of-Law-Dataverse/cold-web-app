<template>
  <UButton :to="to" variant="soft" color="neutral" :class="typeClass">
    <div class="flag-wrapper">
      <JurisdictionFlag :iso3="iso3" class="item-flag" />
    </div>
    <span class="item-title">{{ title }}</span>
    <span class="item-year">{{ year }}</span>
  </UButton>
</template>

<script setup lang="ts">
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";

withDefaults(
  defineProps<{
    to: string;
    iso3: string;
    title: string;
    year: string;
    typeClass?: string;
  }>(),
  {
    typeClass: "",
  },
);
</script>
