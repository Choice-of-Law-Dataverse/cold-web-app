<template>
  <div class="prose flex flex-col gap-2">
    <template v-if="data.domesticLegalProvisions">
      <LegalProvisionRenderer :value="data.domesticLegalProvisions" />
    </template>
    <template v-else-if="data.domesticInstrumentsId">
      <LegalProvisionRenderer
        skip-article
        :value="data.domesticInstrumentsId"
      />
    </template>
    <template v-else>
      <p class="result-value-small">—</p>
    </template>
  </div>
</template>

<script setup lang="ts">
import LegalProvisionRenderer from "@/components/legal/LegalProvisionRenderer.vue";
import type { Question } from "@/types/entities/question";

defineProps<{
  data: Question;
}>();
</script>
