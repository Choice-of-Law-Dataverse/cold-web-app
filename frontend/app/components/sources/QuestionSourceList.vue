<template>
  <div class="prose flex flex-col gap-2">
    <template v-if="data['Domestic Legal Provisions']">
      <LegalProvisionRenderer :value="data['Domestic Legal Provisions']" />
    </template>
    <template v-else-if="data['Domestic Instruments ID']">
      <LegalProvisionRenderer
        skip-article
        :value="data['Domestic Instruments ID']"
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
