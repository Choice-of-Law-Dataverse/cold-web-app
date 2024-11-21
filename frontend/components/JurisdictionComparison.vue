<template>
  <div class="col-span-12">
    <UCard class="cold-ucard">
      <UTable
        v-if="!loading"
        class="styled-table"
        :rows="rows"
        :columns="columns"
      />
      <p v-else>Loading...</p>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  jurisdiction: {
    type: String,
    required: true,
  },
})

const loading = ref(true)
const rows = ref([])
const columns = ref([
  { key: 'Themes', label: 'Themes' },
  { key: 'Questions', label: 'Question' },
  { key: 'Answer', label: props.jurisdiction || 'Answer' }, // Use jurisdiction name as label
])

async function fetchTableData(jurisdiction: string) {
  const payload = {
    table: 'Answers',
    filters: [{ column: 'Name (from Jurisdiction)', value: jurisdiction }],
  }

  try {
    const response = await fetch(
      'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/full_table',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }
    )

    if (!response.ok) throw new Error('Failed to fetch table data')

    const data = await response.json()
    rows.value = data // Populate rows with API response
  } catch (error) {
    console.error('Error fetching table data:', error)
  } finally {
    loading.value = false
  }
}

// Watch for jurisdiction changes
watch(
  () => props.jurisdiction,
  (newJurisdiction) => {
    if (newJurisdiction) {
      loading.value = true
      fetchTableData(newJurisdiction)
    }
  }
)

// Fetch data on component mount
onMounted(() => {
  if (props.jurisdiction) {
    fetchTableData(props.jurisdiction)
  }
})
</script>

<style scoped>
/* Set the row height for all table rows */
.cold-ucard ::v-deep(tbody tr) {
  height: 74px; /* Ensure all rows are 74px high */
}

/* Set the row height for all header rows */
.cold-ucard ::v-deep(thead tr) {
  height: 52px; /* Set the header row height */
}

/* Target deep child classes inside UCard to remove padding */
.cold-ucard ::v-deep(.sm\:p-6) {
  padding: 0 !important;
}

.cold-ucard ::v-deep(.py-5) {
  padding: 0 !important;
}

.cold-ucard ::v-deep(.px-4) {
  padding: 0 !important;
}

/* Ensure the table spans the full width of the card */
.cold-ucard {
  padding: 0; /* Remove padding from UCard */
}

.table-wrapper {
  width: 100%; /* Ensure the table spans the full width of the wrapper */
  overflow-x: auto; /* Handle horizontal scrolling if needed */
}

/* Styling the table rows to indent text on left and right */
.styled-table ::v-deep(tbody tr td),
.styled-table ::v-deep(thead tr th) {
  text-indent: 32px; /* Indent text on the left */
  position: relative; /* Make sure the pseudo-element aligns properly */
}

/* Add indentation for the right side using a pseudo-element */
.styled-table ::v-deep(tbody tr td::after),
.styled-table ::v-deep(thead tr th::after) {
  content: ''; /* Empty content for pseudo-element */
  display: block;
  width: 32px; /* Create space on the right */
  position: absolute;
  right: 0;
  height: 100%;
}
</style>
