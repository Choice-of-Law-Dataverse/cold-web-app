<template>
  <BaseDetailLayout
    table="Arbitral Awards"
    page-heading="Arbitral Awards"
    :loading="isLoading"
    :data="resultData"
  >
    <template #full-width>
      <div class="gradient-top-border" />
      <div class="w-full px-6 py-6">
        <div class="awards-table">
          <UTable :columns="columns" :data="rows">
            <template #caseNumber-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-award/${row.original.coldId}`"
                class="table-row-link"
              >
                <span
                  class="result-value-small block truncate whitespace-nowrap"
                  >{{ row.original.caseNumber }}</span
                >
              </NuxtLink>
              <span
                v-else
                class="result-value-small block truncate whitespace-nowrap"
                >{{ row.original.caseNumber }}</span
              >
            </template>
            <template #year-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-award/${row.original.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{ row.original.year }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{
                row.original.year
              }}</span>
            </template>
            <template #seatTown-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-award/${row.original.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{
                  row.original.seatTown
                }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{
                row.original.seatTown
              }}</span>
            </template>
            <template #source-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-award/${row.original.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{
                  row.original.source
                }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{
                row.original.source
              }}</span>
            </template>
            <template #open-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-award/${row.original.coldId}`"
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
import type { ArbitralAwardResponse } from "@/types/entities/arbitral-award";

useHead({
  title: "Arbitral Awards — CoLD",
});

const { data: rawData, isLoading } = useFullTable("Arbitral Awards");
const resultData = null;

const columns = [
  { id: "caseNumber", accessorKey: "caseNumber", header: "Case Number" },
  { id: "year", accessorKey: "year", header: "Year" },
  { id: "seatTown", accessorKey: "seatTown", header: "Seat (Town)" },
  { id: "source", accessorKey: "source", header: "Source" },
  { id: "open", accessorKey: "coldId", header: "" },
];

const sanitize = (v: string | number | null | undefined) =>
  !v || v === "NA" ? "" : String(v).trim();

const rows = computed(() =>
  (rawData.value || []).map((r: ArbitralAwardResponse) => ({
    caseNumber: sanitize(r.caseNumber),
    year: sanitize(r.year),
    seatTown: sanitize(r.seatTown),
    source: sanitize(r.source),
    coldId: sanitize(r.coldId),
  })),
);
</script>

<style scoped>
.awards-table :deep(table) {
  table-layout: fixed;
  width: 100%;
}

.awards-table :deep(th),
.awards-table :deep(td) {
  box-sizing: border-box;
  width: 125px;
  min-width: 125px;
  max-width: 125px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 16px;
}

.awards-table :deep(th:nth-child(4)),
.awards-table :deep(td:nth-child(4)) {
  width: 225px;
  min-width: 225px;
  max-width: 225px;
}

.awards-table :deep(th:last-child),
.awards-table :deep(td:last-child) {
  padding-right: 16px;
  text-align: right;
}

.awards-table :deep(td:last-child a.label) {
  font-weight: 600;
  font-size: 12px;
}

.awards-table :deep(tbody tr) {
  height: 72px;
}
.awards-table :deep(tbody td) {
  height: 72px;
  vertical-align: top;
}

.awards-table :deep(tbody td:first-child) {
  padding-top: 10px;
}

.awards-table :deep(tbody tr:hover) {
  background-color: rgba(0, 0, 0, 0.02);
  cursor: pointer;
}

.awards-table :deep(tbody tr:hover .arrow-icon) {
  animation: bounce-right 0.4s ease-out;
}

.awards-table :deep(thead th) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.awards-table :deep(thead th span),
.awards-table :deep(thead th button),
.awards-table :deep(thead th button span) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.awards-table :deep(thead th button:hover),
.awards-table :deep(thead th a:hover) {
  background-color: transparent;
  color: inherit;
  text-decoration: none;
  box-shadow: none;
}
.awards-table :deep(thead th button:hover span),
.awards-table :deep(thead th a:hover span) {
  color: inherit;
  text-decoration: none;
}
</style>
