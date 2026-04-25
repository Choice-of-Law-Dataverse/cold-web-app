<template>
  <EntityContent base-path="/international-instrument" :data="data" />
</template>

<script setup lang="ts">
import EntityContent from "@/components/entity/EntityContent.vue";
import type { InternationalInstrument } from "@/types/entities/international-instrument";

defineProps<{
  data: InternationalInstrument;
}>();
</script>
