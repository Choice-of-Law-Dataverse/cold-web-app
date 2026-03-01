<template>
  <BaseDetailLayout
    table="Arbitral Awards"
    :loading="loading"
    :data="resultData"
    :key-label-pairs="computedKeyLabelPairs"
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
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import csvRaw from "./all-arbitral-awards.csv?raw";

useHead({
  title: "Arbitral Awards — CoLD",
});

const loading = false;
const resultData = {} as Record<string, unknown>;
const computedKeyLabelPairs: Record<string, unknown>[] = [];

const columns = [
  { id: "caseNumber", accessorKey: "caseNumber", header: "Case Number" },
  { id: "year", accessorKey: "year", header: "Year" },
  { id: "seatTown", accessorKey: "seatTown", header: "Seat (Town)" },
  { id: "source", accessorKey: "source", header: "Source" },
  { id: "open", accessorKey: "coldId", header: "" },
];

type Row = {
  caseNumber: string;
  year: string;
  seatTown: string;
  source: string;
  coldId: string;
};

function parseCSV(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (inQuotes) {
      if (char === '"') {
        const next = text[i + 1];
        if (next === '"') {
          field += '"';
          i++; // skip the escaped quote
        } else {
          inQuotes = false;
        }
      } else {
        field += char;
      }
    } else {
      if (char === '"') {
        inQuotes = true;
      } else if (char === ",") {
        row.push(field);
        field = "";
      } else if (char === "\n") {
        row.push(field);
        rows.push(row);
        row = [];
        field = "";
      } else if (char !== "\r") {
        field += char;
      }
    }
  }
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  return rows;
}

const csvRows = parseCSV(csvRaw);
const header = csvRows[0] || [];
const idxCase = header.indexOf("Case Number");
const idxYear = header.indexOf("Year");
const idxSeat = header.indexOf("Seat (Town)");
const idxSource = header.indexOf("Source");
const idxColdId = header.indexOf("CoLD ID");

const rows: Row[] = (csvRows.slice(1) || [])
  .map((r) => {
    const get = (idx: number) =>
      idx >= 0 && r[idx] != null ? String(r[idx]).trim() : "";
    const sanitize = (v: string) => (v === "NA" ? "" : v);
    return {
      caseNumber: sanitize(get(idxCase)),
      year: sanitize(get(idxYear)),
      seatTown: sanitize(get(idxSeat)),
      source: sanitize(get(idxSource)),
      coldId: sanitize(get(idxColdId)),
    };
  })
  .filter((r) => r.caseNumber || r.year || r.seatTown || r.source || r.coldId);
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

/* Row hover effects */
.awards-table :deep(tbody tr:hover) {
  background-color: rgba(0, 0, 0, 0.02);
  cursor: pointer;
}

/* Trigger arrow bounce animation on row hover */
.awards-table :deep(tbody tr:hover .arrow-icon) {
  animation: bounce-right 0.4s ease-out;
}

/* Style header titles to visually resemble `.label` without breaking sorting */
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
