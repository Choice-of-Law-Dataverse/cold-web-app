<template>
  <BaseDetailLayout
    table="Arbitral Rules"
    :loading="isLoading"
    :data="resultData"
  >
    <template #full-width>
      <div class="gradient-top-border" />
      <div class="w-full px-6 py-6">
        <div class="rules-table" :style="{ '--set-col-width': setColWidth }">
          <UTable :columns="columns" :data="rows">
            <template #setOfRules-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-rule/${row.original.coldId}`"
                class="table-row-link"
              >
                <span
                  class="result-value-small block truncate whitespace-nowrap"
                  >{{ row.original.setOfRules }}</span
                >
              </NuxtLink>
              <span
                v-else
                class="result-value-small block truncate whitespace-nowrap"
                >{{ row.original.setOfRules }}</span
              >
            </template>
            <template #inForceFrom-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-rule/${row.original.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{
                  formatDate(row.original.inForceFrom) || ""
                }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{
                formatDate(row.original.inForceFrom) || ""
              }}</span>
            </template>
            <template #open-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-rule/${row.original.coldId}`"
                class="table-row-link arrow-cell"
              >
                <UIcon
                  name="i-material-symbols:arrow-forward"
                  class="arrow-icon"
                />
              </NuxtLink>
              <span v-else class="text-gray-400">—</span>
            </template>
          </UTable>
        </div>
      </div>
    </template>
  </BaseDetailLayout>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import { useFullTable } from "@/composables/useFullTable";
import { formatDate } from "@/utils/format";
import type { ArbitralRuleResponse } from "@/types/entities/arbitral-rule";

useHead({
  title: "Arbitral Rules — CoLD",
});

const { data: rawData, isLoading } = useFullTable("Arbitral Rules");
const resultData = null;

const columns = [
  { id: "setOfRules", accessorKey: "setOfRules", header: "Set of Rules" },
  { id: "inForceFrom", accessorKey: "inForceFrom", header: "In Force From" },
  { id: "open", accessorKey: "coldId", header: "" },
];

const sanitize = (v: string | number | null | undefined) =>
  !v || v === "NA" ? "" : String(v).trim();

const rows = computed(() =>
  (rawData.value || []).map((r: ArbitralRuleResponse) => ({
    setOfRules: sanitize(r.setOfRules),
    inForceFrom: sanitize(r.inForceFrom),
    coldId: sanitize(r.coldId),
  })),
);

const setColWidth = ref<string>("125px");

function computeSetOfRulesColumnWidth() {
  if (typeof window === "undefined") return;
  try {
    const temp = document.createElement("span");
    temp.className = "result-value-small";
    temp.style.visibility = "hidden";
    temp.style.position = "absolute";
    temp.style.whiteSpace = "nowrap";
    document.body.appendChild(temp);
    const cs = getComputedStyle(temp);
    document.body.removeChild(temp);

    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;

    let max = 0;
    for (const r of rows.value) {
      const text = r.setOfRules || "";
      const m = ctx.measureText(text);
      max = Math.max(max, m.width);
    }
    const px = Math.ceil(max + 28);
    setColWidth.value = `${px}px`;
  } catch {
    setColWidth.value = "225px";
  }
}

watch(rows, (val) => {
  if (val.length > 0) computeSetOfRulesColumnWidth();
});
</script>

<style scoped>
.rules-table :deep(table) {
  table-layout: fixed;
  width: 100%;
}

.rules-table :deep(th),
.rules-table :deep(td) {
  box-sizing: border-box;
  width: 125px;
  min-width: 125px;
  max-width: 125px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 16px;
}

.rules-table :deep(th:first-child),
.rules-table :deep(td:first-child) {
  width: var(--set-col-width);
  min-width: var(--set-col-width);
  max-width: var(--set-col-width);
}

.rules-table :deep(th:nth-child(4)),
.rules-table :deep(td:nth-child(4)) {
  width: 225px;
  min-width: 225px;
  max-width: 225px;
}

.rules-table :deep(th:last-child),
.rules-table :deep(td:last-child) {
  padding-right: 16px;
  text-align: right;
}

.rules-table :deep(td:last-child a.label) {
  font-weight: 600;
  font-size: 12px;
}

.rules-table :deep(tbody tr) {
  height: 72px;
}
.rules-table :deep(tbody td) {
  height: 72px;
  vertical-align: top;
}

.rules-table :deep(tbody td:first-child) {
  padding-top: 10px;
}

.rules-table :deep(tbody tr:hover) {
  background-color: rgba(0, 0, 0, 0.02);
  cursor: pointer;
}

.rules-table :deep(tbody tr:hover .arrow-icon) {
  animation: bounce-right 0.4s ease-out;
}

.rules-table :deep(thead th) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.rules-table :deep(thead th span),
.rules-table :deep(thead th button),
.rules-table :deep(thead th button span) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.rules-table :deep(thead th button:hover),
.rules-table :deep(thead th a:hover) {
  background-color: transparent;
  color: inherit;
  text-decoration: none;
  box-shadow: none;
}
.rules-table :deep(thead th button:hover span),
.rules-table :deep(thead th a:hover span) {
  color: inherit;
  text-decoration: none;
}
</style>
