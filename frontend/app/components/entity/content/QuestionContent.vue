<template>
  <EntityContent base-path="/question" :data="data">
    <template #answer="{ value, label, tooltip }">
      <section v-if="value">
        <DetailRow :label="label" :tooltip="tooltip">
          <ResultValue size="md" as="p" class="whitespace-pre-line">{{
            value
          }}</ResultValue>
        </DetailRow>
      </section>
    </template>
  </EntityContent>
</template>

<script setup lang="ts">
import EntityContent from "@/components/entity/EntityContent.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import type { Question } from "@/types/entities/question";
import ResultValue from "@/components/ui/ResultValue.vue";

defineProps<{
  data: Question;
}>();
</script>
