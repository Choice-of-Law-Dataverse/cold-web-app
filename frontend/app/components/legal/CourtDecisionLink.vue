<template>
  <BaseLegalLink :to="`/court-decision/${caseId}`" :class="props.class">
    {{ caseId }}
  </BaseLegalLink>
</template>

<script setup lang="ts">
import BaseLegalLink from "@/components/legal/BaseLegalLink.vue";

const props = defineProps<{
  caseId: string;
  class?: string;
}>();
</script>
