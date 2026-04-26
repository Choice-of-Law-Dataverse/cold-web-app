<template>
  <BaseDetailLayout
    table="Arbitral Institutions"
    page-heading="Arbitral Institutions"
    :loading="isLoading"
    :data="resultData"
  >
    <template #full-width>
      <div class="gradient-top-border" />
      <div class="w-full px-6 py-6">
        <div class="institutions-table">
          <UTable :columns="columns" :data="rows">
            <template #institution-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-institution/${row.original.coldId}`"
                class="table-row-link"
              >
                <span
                  class="result-value-small block truncate whitespace-nowrap"
                  >{{ row.original.institution }}</span
                >
              </NuxtLink>
              <span
                v-else
                class="result-value-small block truncate whitespace-nowrap"
                >{{ row.original.institution }}</span
              >
            </template>
            <template #abbreviation-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-institution/${row.original.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{
                  row.original.abbreviation
                }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{
                row.original.abbreviation
              }}</span>
            </template>
            <template #open-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-institution/${row.original.coldId}`"
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
import { computed } from "vue";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import { useFullTable } from "@/composables/useFullTable";
import type { ArbitralInstitutionResponse } from "@/types/entities/arbitral-institution";

useHead({
  title: "Arbitral Institutions — CoLD",
});

const { data: rawData, isLoading } = useFullTable("Arbitral Institutions");
const resultData = null;

const columns = [
  { id: "institution", accessorKey: "institution", header: "Institution" },
  { id: "abbreviation", accessorKey: "abbreviation", header: "Abbreviation" },
  { id: "open", accessorKey: "coldId", header: "" },
];

const sanitize = (v: string | number | null | undefined) =>
  !v || v === "NA" ? "" : String(v).trim();

const rows = computed(() =>
  (rawData.value || []).map((r: ArbitralInstitutionResponse) => ({
    institution: sanitize(r.institution),
    abbreviation: sanitize(r.abbreviation),
    coldId: sanitize(r.coldId),
  })),
);
</script>

<style scoped>
.institutions-table :deep(table) {
  table-layout: fixed;
  width: 100%;
}

.institutions-table :deep(th),
.institutions-table :deep(td) {
  box-sizing: border-box;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 16px;
}

.institutions-table :deep(th:first-child),
.institutions-table :deep(td:first-child) {
  width: 50%;
}

.institutions-table :deep(th:nth-child(2)),
.institutions-table :deep(td:nth-child(2)) {
  width: 200px;
  min-width: 200px;
  max-width: 200px;
}

.institutions-table :deep(th:last-child),
.institutions-table :deep(td:last-child) {
  padding-right: 16px;
  text-align: right;
}

.institutions-table :deep(td:last-child a.label) {
  font-weight: 600;
  font-size: 12px;
}

.institutions-table :deep(tbody tr) {
  height: 72px;
}
.institutions-table :deep(tbody td) {
  height: 72px;
  vertical-align: top;
}

.institutions-table :deep(tbody td:first-child) {
  padding-top: 10px;
}

.institutions-table :deep(tbody tr:hover) {
  background-color: rgba(0, 0, 0, 0.02);
  cursor: pointer;
}

.institutions-table :deep(tbody tr:hover .arrow-icon) {
  animation: bounce-right 0.4s ease-out;
}

.institutions-table :deep(thead th) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.institutions-table :deep(thead th span),
.institutions-table :deep(thead th button),
.institutions-table :deep(thead th button span) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.institutions-table :deep(thead th button:hover),
.institutions-table :deep(thead th a:hover) {
  background-color: transparent;
  color: inherit;
  text-decoration: none;
  box-shadow: none;
}
.institutions-table :deep(thead th button:hover span),
.institutions-table :deep(thead th a:hover span) {
  color: inherit;
  text-decoration: none;
}
</style>
