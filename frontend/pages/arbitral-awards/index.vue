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
        <UTable :columns="columns" :rows="rows" />
      </div>
    </template>
  </BaseDetailLayout>
</template>

<script setup lang="ts">
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
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
]

type Row = { caseNumber: string; year: string; seatTown: string }

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

const rows: Row[] = (csvRows.slice(1) || [])
  .map((r) => {
    const get = (idx: number) =>
      idx >= 0 && r[idx] != null ? String(r[idx]).trim() : ''
    const sanitize = (v: string) => (v === 'NA' ? '' : v)
    return {
      caseNumber: sanitize(get(idxCase)),
      year: sanitize(get(idxYear)),
      seatTown: sanitize(get(idxSeat)),
    }
  })
  .filter((r) => r.caseNumber || r.year || r.seatTown)
</script>
