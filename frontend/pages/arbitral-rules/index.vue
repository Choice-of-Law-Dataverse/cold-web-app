<template>
  <!-- Use the shared detail layout to match spacing, container width, and card styling. -->
  <!-- Use sourceTable="Loading" so the header stays hidden, yielding a clean blank card. -->
  <BaseDetailLayout
    :loading="loading"
    :result-data="resultData"
    :key-label-pairs="computedKeyLabelPairs"
    :value-class-map="valueClassMap"
    source-table="Arbitral Rule"
  >
    <template #full-width>
      <div class="px-6 py-6">
        <h1 class="mb-6">Arbitral Rules</h1>
        <div class="rules-table" :style="{ '--set-col-width': setColWidth }">
          <UTable :columns="columns" :rows="rows">
            <template #setofRules-data="{ row }">
              <span
                class="result-value-small block truncate whitespace-nowrap"
                >{{ row.setofRules }}</span
              >
            </template>
            <template #inForceFrom-data="{ row }">
              <span class="result-value-small">{{
                formatDate(row.inForceFrom) || ""
              }}</span>
            </template>
            <template #open-data="{ row }">
              <NuxtLink
                v-if="row.coldId"
                :to="`/arbitral-rule/${row.coldId}`"
                class="label result-value-small font-semibold"
              >
                Open
                <UIcon
                  name="i-material-symbols:play-arrow"
                  class="-mb-[1px] inline-block"
                />
              </NuxtLink>
              <span v-else class="text-gray-300">—</span>
            </template>
          </UTable>
        </div>
      </div>
    </template>
  </BaseDetailLayout>
</template>

<script setup lang="ts">
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import { ref, onMounted } from "vue";
import { formatDate } from "@/utils/format";
// Using static CSV downloaded from NocoDB because API does not provide arbitral rules
import csvRaw from "./all-arbitral-rules.csv?raw";

useHead({
  title: "Arbitral Rules — CoLD",
});

// Minimal props for BaseDetailLayout to render a blank card with the same layout
const loading = false;
const resultData = {} as Record<string, unknown>;
const computedKeyLabelPairs: Record<string, unknown>[] = [];
const valueClassMap: Record<string, string> = {};

// Columns to display from CSV
const columns = [
  { key: "setofRules", label: "Set of Rules", sortable: true },
  { key: "inForceFrom", label: "In Force From", sortable: true },
  { key: "open", label: "" },
];

type Row = {
  setofRules: string;
  inForceFrom: string;
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
      } else if (char === "\r") {
        // ignore
      } else {
        field += char;
      }
    }
  }
  // push last field/row if any
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  return rows;
}

const csvRows = parseCSV(csvRaw);
const header = csvRows[0] || [];
const idxSet = header.indexOf("Set of Rules");
const idxinForceFrom = header.indexOf("In Force From");
const idxColdId = header.indexOf("CoLD ID");

const rows: Row[] = (csvRows.slice(1) || [])
  .map((r) => {
    const get = (idx: number) =>
      idx >= 0 && r[idx] != null ? String(r[idx]).trim() : "";
    const sanitize = (v: string) => (v === "NA" ? "" : v);
    return {
      setofRules: sanitize(get(idxSet)),
      inForceFrom: sanitize(get(idxinForceFrom)),
      coldId: sanitize(get(idxColdId)),
    };
  })
  .filter((r) => r.setofRules || r.inForceFrom || r.coldId);

// Dynamically size the first column (Set of Rules) to the longest string
const setColWidth = ref<string>("125px");

function computeSetOfRulesColumnWidth() {
  if (typeof window === "undefined") return;
  try {
    // Create a temp element to capture the font used by result-value-small
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
    for (const r of rows) {
      const text = r.setofRules || "";
      const m = ctx.measureText(text);
      max = Math.max(max, m.width);
    }
    // Add padding/gutter allowance and a small buffer
    const px = Math.ceil(max + 28);
    setColWidth.value = `${px}px`;
  } catch {
    setColWidth.value = "225px";
  }
}

onMounted(() => {
  computeSetOfRulesColumnWidth();
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
  width: 125px !important;
  min-width: 125px !important;
  max-width: 125px !important;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 16px !important; /* column gutter */
}

/* Make the first column (Set of Rules) width match the longest string */
.rules-table :deep(th:first-child),
.rules-table :deep(td:first-child) {
  width: var(--set-col-width) !important;
  min-width: var(--set-col-width) !important;
  max-width: var(--set-col-width) !important;
}

/* Make the Source column 100px wider (125px + 100px = 225px) */
.rules-table :deep(th:nth-child(4)),
.rules-table :deep(td:nth-child(4)) {
  width: 225px !important;
  min-width: 225px !important;
  max-width: 225px !important;
}

.rules-table :deep(th:last-child),
.rules-table :deep(td:last-child) {
  padding-right: 0 !important; /* no gutter after last column */
  text-align: right !important; /* align Open column to the right */
}

/* Ensure the "Open" link uses font-weight 600 even if .label sets 700 */
.rules-table :deep(td:last-child a.label) {
  font-weight: 600 !important;
  font-size: 12px !important;
}

/* Increase data row height to 72px and vertically center content */
.rules-table :deep(tbody tr) {
  height: 72px !important;
}
.rules-table :deep(tbody td) {
  height: 72px !important;
  vertical-align: top !important;
}

/* Remove top padding from the first column (Set of Rules) to avoid visual offset */
.rules-table :deep(tbody td:first-child) {
  padding-top: 10px !important;
}

/* Style header titles to visually resemble `.label` without breaking sorting */
.rules-table :deep(thead th) {
  font-weight: 700 !important; /* similar to .label */
  font-size: 12px !important; /* similar sizing */
  letter-spacing: 0.01em;
  text-transform: uppercase !important;
  color: var(--color-cold-night);
}
/* Stronger override for frameworks that style inner elements */
.rules-table :deep(thead th span),
.rules-table :deep(thead th button),
.rules-table :deep(thead th button span) {
  font-weight: 700 !important;
  font-size: 12px !important;
  letter-spacing: 0.01em !important;
  text-transform: uppercase !important;
  color: var(--color-cold-night);
}

/* Remove hover effect on header titles but keep sorting clickable */
.rules-table :deep(thead th button:hover),
.rules-table :deep(thead th a:hover) {
  background-color: transparent !important;
  color: inherit !important;
  text-decoration: none !important;
  box-shadow: none !important;
}
.rules-table :deep(thead th button:hover span),
.rules-table :deep(thead th a:hover span) {
  color: inherit !important;
  text-decoration: none !important;
}
</style>
