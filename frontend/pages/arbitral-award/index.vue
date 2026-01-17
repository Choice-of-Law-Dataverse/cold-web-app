<template>
  <BaseDetailLayout
    :loading="loading"
    :result-data="resultData"
    :key-label-pairs="computedKeyLabelPairs"
    :value-class-map="valueClassMap"
    source-table="Arbitral Award"
  >
    <template #full-width>
      <div class="gradient-top-border w-full">
      <div class="px-6 py-6">
        <h1 class="mb-6">Arbitral Awards</h1>
        <div class="awards-table">
          <UTable :columns="columns" :rows="rows">
            <template #caseNumber-data="{ row }">
              <NuxtLink
                v-if="row.coldId"
                :to="`/arbitral-award/${row.coldId}`"
                class="table-row-link"
              >
                <span
                  class="result-value-small block truncate whitespace-nowrap"
                  >{{ row.caseNumber }}</span
                >
              </NuxtLink>
              <span
                v-else
                class="result-value-small block truncate whitespace-nowrap"
                >{{ row.caseNumber }}</span
              >
            </template>
            <template #year-data="{ row }">
              <NuxtLink
                v-if="row.coldId"
                :to="`/arbitral-award/${row.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{ row.year }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{ row.year }}</span>
            </template>
            <template #seatTown-data="{ row }">
              <NuxtLink
                v-if="row.coldId"
                :to="`/arbitral-award/${row.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{ row.seatTown }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{ row.seatTown }}</span>
            </template>
            <template #source-data="{ row }">
              <NuxtLink
                v-if="row.coldId"
                :to="`/arbitral-award/${row.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{ row.source }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{ row.source }}</span>
            </template>
            <template #open-data="{ row }">
              <NuxtLink
                v-if="row.coldId"
                :to="`/arbitral-award/${row.coldId}`"
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
      </div>  
    </template>
  </BaseDetailLayout>
</template>

<script setup lang="ts">
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import csvRaw from "./all-arbitral-awards.csv?raw";

useHead({
  title: "Arbitral Awards — CoLD",
});

const loading = false;
const resultData = {} as Record<string, unknown>;
const computedKeyLabelPairs: Record<string, unknown>[] = [];
const valueClassMap: Record<string, string> = {};

const columns = [
  { key: "caseNumber", label: "Case Number", sortable: true },
  { key: "year", label: "Year", sortable: true },
  { key: "seatTown", label: "Seat (Town)", sortable: true },
  { key: "source", label: "Source", sortable: false },
  { key: "open", label: "" },
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
  width: 125px !important;
  min-width: 125px !important;
  max-width: 125px !important;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 16px !important; /* column gutter */
}

/* Make the Source column 100px wider (125px + 100px = 225px) */
.awards-table :deep(th:nth-child(4)),
.awards-table :deep(td:nth-child(4)) {
  width: 225px !important;
  min-width: 225px !important;
  max-width: 225px !important;
}

.awards-table :deep(th:last-child),
.awards-table :deep(td:last-child) {
  padding-right: 16px !important; /* Add padding to prevent animation cutoff */
  text-align: right !important; /* align Open column to the right */
}

/* Ensure the "Open" link uses font-weight 600 even if .label sets 700 */
.awards-table :deep(td:last-child a.label) {
  font-weight: 600 !important;
  font-size: 12px !important;
}

/* Increase data row height to 72px and vertically center content */
.awards-table :deep(tbody tr) {
  height: 72px !important;
}
.awards-table :deep(tbody td) {
  height: 72px !important;
  vertical-align: top !important;
}

/* Remove top padding from the first column (Case Number) to avoid visual offset */
.awards-table :deep(tbody td:first-child) {
  padding-top: 10px !important;
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
  font-weight: 700 !important; /* similar to .label */
  font-size: 12px !important; /* similar sizing */
  letter-spacing: 0.01em;
  text-transform: uppercase !important;
  color: var(--color-cold-night);
}
/* Stronger override for frameworks that style inner elements */
.awards-table :deep(thead th span),
.awards-table :deep(thead th button),
.awards-table :deep(thead th button span) {
  font-weight: 700 !important;
  font-size: 12px !important;
  letter-spacing: 0.01em !important;
  text-transform: uppercase !important;
  color: var(--color-cold-night);
}

/* Remove hover effect on header titles but keep sorting clickable */
.awards-table :deep(thead th button:hover),
.awards-table :deep(thead th a:hover) {
  background-color: transparent !important;
  color: inherit !important;
  text-decoration: none !important;
  box-shadow: none !important;
}
.awards-table :deep(thead th button:hover span),
.awards-table :deep(thead th a:hover span) {
  color: inherit !important;
  text-decoration: none !important;
}
</style>
