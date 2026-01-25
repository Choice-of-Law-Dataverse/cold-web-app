<template>
  <BaseLegalRenderer
    :items="value"
    :value-class-map="valueClassMap"
    :empty-value-behavior="emptyValueBehavior"
    default-class="result-value-small"
    wrapper-class="flex flex-wrap gap-2"
  >
    <template #default="{ item }">
      <NuxtLink
        class="link-chip--neutral"
        :to="`/court-decision/${item as string}`"
      >
        <template v-if="decisionsById.get(item as string)">
          {{ decisionsById.get(item as string)!.displayTitle }}
        </template>
        <template v-else-if="decisionsError">
          {{ item }}
        </template>
        <template v-else>
          <LoadingBar />
        </template>
      </NuxtLink>
    </template>
  </BaseLegalRenderer>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useCourtDecisionsList } from "@/composables/useRecordDetails";
import type { CourtDecision } from "@/types/entities/court-decision";
import BaseLegalRenderer from "./BaseLegalRenderer.vue";
import { NuxtLink } from "#components";
import LoadingBar from "@/components/layout/LoadingBar.vue";

const props = withDefaults(
  defineProps<{
    value: string[] | string;
    valueClassMap?: string;
    emptyValueBehavior?: {
      action: string;
      fallback: string;
    };
  }>(),
  {
    valueClassMap: "",
    emptyValueBehavior: () => ({
      action: "display",
      fallback: "—",
    }),
  },
);

const decisionIds = computed(() => {
  const items = Array.isArray(props.value) ? props.value : [props.value];
  return [...new Set(items.filter(Boolean))];
});

const { data: decisions, error: decisionsError } =
  useCourtDecisionsList(decisionIds);

const decisionsById = computed(() => {
  const map = new Map<string, CourtDecision>();
  if (!decisions.value) return map;
  for (const rec of decisions.value) {
    if (rec) map.set(rec.id, rec);
  }
  return map;
});
</script>
