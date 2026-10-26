<template>
  <EntityLink
    :id="id ?? iso3"
    :title="label"
    :base-path="basePath"
    variant="jurisdiction"
  >
    <div class="flag-wrapper">
      <JurisdictionFlag :iso3="iso3" class="item-flag" :alt="`${label} flag`" />
    </div>
    {{ label }}
  </EntityLink>
</template>

<script setup lang="ts">
import EntityLink from "@/components/ui/EntityLink.vue";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";

withDefaults(
  defineProps<{
    /** ISO 3166-1 alpha-3 code that selects the flag */
    iso3: string;
    label: string;
    /** Target entity id; defaults to the jurisdiction itself */
    id?: string;
    basePath?: string;
  }>(),
  {
    id: undefined,
    basePath: "/jurisdiction",
  },
);
</script>
