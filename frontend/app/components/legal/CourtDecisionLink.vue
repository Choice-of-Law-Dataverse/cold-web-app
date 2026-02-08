<template>
  <div>
    <NuxtLink
      :to="`/court-decision/${caseId}`"
      :class="['result-value-small', props.class]"
    >
      {{ caseId }}
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  caseId: string;
  class?: string;
}>();
</script>
