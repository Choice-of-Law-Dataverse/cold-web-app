<template>
  <EntityContent base-path="/specialist" :data="data">
    <template #website="{ value, label }">
      <DetailRow :label="label">
        <a
          :href="String(value)"
          target="_blank"
          rel="noopener noreferrer"
          class="text-primary break-all hover:underline"
        >
          {{ value }}
        </a>
      </DetailRow>
    </template>
  </EntityContent>
</template>

<script setup lang="ts">
import EntityContent from "@/components/entity/EntityContent.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import type { Specialist } from "@/types/entities/specialist";

defineProps<{
  data: Specialist;
}>();
</script>
