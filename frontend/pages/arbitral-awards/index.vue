<template>
  <!-- Use the shared detail layout to match spacing, container width, and card styling. -->
  <!-- Use sourceTable="Loading" so the header stays hidden, yielding a clean blank card. -->
  <BaseDetailLayout
    :loading="loading"
    :resultData="resultData"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Arbitral Award"
  >
    <template #full-width>
      <div class="px-6 py-6">
        <h1 class="mb-6">Arbitral Awards</h1>
        <div class="awards-table">
          <UTable
            :columns="columns"
            :rows="rows"
            :ui="{
              th: {
                base: 'first:w-[150px] first:min-w-[150px] first:max-w-[150px]',
              },
              td: {
                base: 'first:w-[150px] first:min-w-[150px] first:max-w-[150px]',
              },
            }"
          >
            <template #caseNumber-data="{ row }">
              <span class="block truncate whitespace-nowrap">{{
                row.caseNumber
              }}</span>
            </template>
          </UTable>
        </div>
      </div>
    </template>
  </BaseDetailLayout>
</template>

<script setup lang="ts">
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
// Using static CSV because API does not provide arbitral awards
import csvRaw from './all-arbitral-awards.csv?raw'

useHead({
  title: 'Arbitral Awards — CoLD',
})

// Minimal props for BaseDetailLayout to render a blank card with the same layout
const loading = false
const resultData = {} as any
const computedKeyLabelPairs: any[] = []
const valueClassMap: Record<string, string> = {}

// Columns to display from CSV
const columns = [
  { key: 'caseNumber', label: 'Case Number', sortable: true },
  { key: 'year', label: 'Year', sortable: true },
  { key: 'seatTown', label: 'Seat (Town)', sortable: true },
  { key: 'source', label: 'Source', sortable: true },
]

type Row = {
  caseNumber: string
  year: string
  seatTown: string
  source: string
}

function parseCSV(text: string): string[][] {
  const rows: string[][] = []
  let row: string[] = []
  let field = ''
  let inQuotes = false

  for (let i = 0; i < text.length; i++) {
    const char = text[i]
    if (inQuotes) {
      if (char === '"') {
        const next = text[i + 1]
        if (next === '"') {
          field += '"'
          i++ // skip the escaped quote
        } else {
          inQuotes = false
        }
      } else {
        field += char
      }
    } else {
      if (char === '"') {
        inQuotes = true
      } else if (char === ',') {
        row.push(field)
        field = ''
      } else if (char === '\n') {
        row.push(field)
        rows.push(row)
        row = []
        field = ''
      } else if (char === '\r') {
        // ignore
      } else {
        field += char
      }
    }
  }
  // push last field/row if any
  if (field.length > 0 || row.length > 0) {
    row.push(field)
    rows.push(row)
  }
  return rows
}

const csvRows = parseCSV(csvRaw)
const header = csvRows[0] || []
const idxCase = header.indexOf('Case Number')
const idxYear = header.indexOf('Year')
const idxSeat = header.indexOf('Seat (Town)')
const idxSource = header.indexOf('Source')

const rows: Row[] = (csvRows.slice(1) || [])
  .map((r) => {
    const get = (idx: number) =>
      idx >= 0 && r[idx] != null ? String(r[idx]).trim() : ''
    const sanitize = (v: string) => (v === 'NA' ? '' : v)
    return {
      caseNumber: sanitize(get(idxCase)),
      year: sanitize(get(idxYear)),
      seatTown: sanitize(get(idxSeat)),
      source: sanitize(get(idxSource)),
    }
  })
  .filter((r) => r.caseNumber || r.year || r.seatTown || r.source)
</script>

<style scoped>
.awards-table :deep(table) {
  table-layout: fixed;
  width: 100%;
}

.awards-table :deep(th:first-child),
.awards-table :deep(td:first-child) {
  box-sizing: border-box;
  width: 150px !important;
  min-width: 150px !important;
  max-width: 150px !important;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
