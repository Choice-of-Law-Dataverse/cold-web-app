<template>
  <div>
    <div v-if="hasContent">
      <div
        v-if="normalizedItems.length > 1"
        :class="props.valueClassMap || 'result-value-small'"
        class="flex flex-wrap gap-2"
      >
        <UButton
          v-for="(item, index) in normalizedItems"
          :key="index"
          variant="ghost"
          color="neutral"
          class="link-chip--neutral"
          :to="`/court-decision/${item}`"
        >
          <template v-if="decisionsById.get(item)">
            {{ decisionsById.get(item)!.displayTitle }}
          </template>
          <template v-else-if="decisionsError">
            {{ item }}
          </template>
          <template v-else>
            <LoadingBar />
          </template>
        </UButton>
      </div>
      <div v-else :class="props.valueClassMap || 'result-value-small'">
        <UButton
          variant="ghost"
          color="neutral"
          class="link-chip--neutral"
          :to="`/court-decision/${normalizedItems[0]!}`"
        >
          <template v-if="decisionsById.get(normalizedItems[0]!)">
            {{ decisionsById.get(normalizedItems[0]!)!.displayTitle }}
          </template>
          <template v-else-if="decisionsError">
            {{ normalizedItems[0] }}
          </template>
          <template v-else>
            <LoadingBar />
          </template>
        </UButton>
      </div>
    </div>
    <div
      v-else-if="displayValue"
      :class="props.valueClassMap || 'result-value-small'"
    >
      {{ displayValue }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useCourtDecisionsList } from "@/composables/useRecordDetails";
import type { CourtDecision } from "@/types/entities/court-decision";
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

const normalizedItems = computed(() => {
  const items = Array.isArray(props.value) ? props.value : [props.value];
  return items.filter(Boolean);
});

const hasContent = computed(() => normalizedItems.value.length > 0);

const displayValue = computed(() => {
  if (hasContent.value) return null;
  if (props.emptyValueBehavior.action === "hide") return null;
  return props.emptyValueBehavior.fallback;
});

const decisionIds = computed(() => [...new Set(normalizedItems.value)]);

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
