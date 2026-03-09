<template>
  <div class="flex flex-col gap-2">
    <slot name="before-fields" />

    <template v-for="field in resolvedFields" :key="field.key">
      <template v-if="$slots[field.key]">
        <slot
          :name="field.key"
          :value="data[field.key]"
          :label="field.label"
          :tooltip="field.tooltip"
        />
      </template>
      <section v-else-if="shouldDisplayValue(data[field.key])">
        <DetailRow
          :label="field.label"
          :tooltip="field.tooltip"
          :variant="resolvedVariant"
        >
          <p class="result-value-small whitespace-pre-line">
            {{ formatValue(data[field.key]) }}
          </p>
        </DetailRow>
      </section>
    </template>

    <slot name="after-fields" />

    <template v-for="section in resolvedRelations" :key="section.key">
      <section v-if="section.items.length > 0">
        <DetailRow :label="section.label" :variant="section.variant">
          <RelatedItemsList
            :items="section.items"
            :base-path="section.basePath"
          />
        </DetailRow>
      </section>
    </template>

    <slot name="after-relations" />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { camelCaseToLabel } from "@/utils/camelCaseToLabel";
import { formatDate } from "@/utils/format";
import { tooltips } from "@/config/tooltips";
import {
  getEntityConfig,
  RELATION_RENDERERS,
  mapRelationToItem,
} from "@/config/entityRegistry";
import type { RelatedItem } from "@/types/ui";
import DetailRow from "@/components/ui/DetailRow.vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";

interface ResolvedField {
  key: string;
  label: string;
  tooltip?: string;
}

interface ResolvedRelation {
  key: string;
  label: string;
  basePath: string;
  variant?: string;
  items: RelatedItem[];
}

const props = withDefaults(
  defineProps<{
    data: Record<string, unknown>;
    basePath?: string;
    fieldOrder?: string[];
    labelOverrides?: Record<string, string>;
    relations?: Record<string, Record<string, unknown>[]>;
    excludeRelations?: Set<string>;
    variant?: string;
  }>(),
  {
    basePath: undefined,
    fieldOrder: () => [],
    labelOverrides: () => ({}),
    relations: undefined,
    excludeRelations: undefined,
    variant: undefined,
  },
);

const entityConfig = computed(() =>
  props.basePath ? getEntityConfig(props.basePath) : undefined,
);

const resolvedFieldOrder = computed(
  () => entityConfig.value?.fieldOrder ?? props.fieldOrder ?? [],
);

const resolvedLabelOverrides = computed(
  () => entityConfig.value?.labelOverrides ?? props.labelOverrides ?? {},
);

const resolvedVariant = computed(
  () => entityConfig.value?.variant ?? props.variant,
);

const resolvedRelationsData = computed(
  () =>
    props.relations ??
    (props.data.relations as
      | Record<string, Record<string, unknown>[]>
      | undefined),
);

const resolvedFields = computed<ResolvedField[]>(() =>
  resolvedFieldOrder.value.map((key) => ({
    key,
    label: resolvedLabelOverrides.value[key] ?? camelCaseToLabel(key),
    tooltip: tooltips[key],
  })),
);

const resolvedRelations = computed<ResolvedRelation[]>(() => {
  const relData = resolvedRelationsData.value;
  if (!relData) return [];
  const exclude = props.excludeRelations ?? new Set<string>();
  return Object.entries(RELATION_RENDERERS)
    .filter(([key]) => !exclude.has(key))
    .map(([key, config]) => {
      const rawItems = relData[key] ?? [];
      const sorted = [...rawItems].sort(
        (a, b) =>
          (Number(a.rankingDisplayOrder) || 0) -
          (Number(b.rankingDisplayOrder) || 0),
      );
      return {
        key,
        ...config,
        items: sorted.map(mapRelationToItem).filter((item) => item.id),
      };
    })
    .filter((s) => s.items.length > 0);
});

function shouldDisplayValue(value: unknown): boolean {
  if (value === null || value === undefined) return false;
  if (value === "NA" || value === "N/A") return false;
  if (Array.isArray(value) && value.length === 0) return false;
  if (typeof value === "string" && value.trim() === "") return false;
  return true;
}

const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2})?/;

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "\u2014";
  if (Array.isArray(value)) {
    if (value.length === 0) return "\u2014";
    if (typeof value[0] === "string") return value.join(", ");
    return String(value.length) + " items";
  }
  if (typeof value === "string" && ISO_DATE_RE.test(value)) {
    return formatDate(value) ?? "\u2014";
  }
  return String(value);
}
</script>
