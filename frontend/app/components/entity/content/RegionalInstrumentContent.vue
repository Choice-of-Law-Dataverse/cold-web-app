<template>
  <EntityContent base-path="/regional-instrument" :data="data" />
</template>

<script setup lang="ts">
import EntityContent from "@/components/entity/EntityContent.vue";
import type { RegionalInstrument } from "@/types/entities/regional-instrument";

defineProps<{
  data: RegionalInstrument;
}>();
</script>
