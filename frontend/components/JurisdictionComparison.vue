<template>
  <div class="col-span-12">
    <UCard class="cold-ucard">
      <UTable
        v-if="!loading"
        class="styled-table"
        :rows="rows"
        :columns="columns"
        :ui="{
          th: {
            base: 'text-left rtl:text-right',
            padding: 'px-8 py-3.5' /* Adjust horizontal and vertical padding */,
            color: 'text-gray-900 dark:text-white',
            font: 'font-semibold',
            size: 'text-sm',
          },
          td: {
            padding: 'px-8 py-2' /* Optionally adjust padding for data cells */,
          },
        }"
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
  { key: 'Themes', label: 'Theme', class: 'label' },
  { key: 'Questions', label: 'Question', class: 'label' },
  { key: 'Answer', label: props.jurisdiction || 'Answer', class: 'label' },
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
::v-deep(thead th:nth-child(1)),
::v-deep(tbody td:nth-child(1)) {
  width: 200px !important; /* Set fixed width */
  max-width: 200px !important; /* Prevent expansion */
  white-space: normal; /* Allow text wrapping */
  /*word-wrap: break-word; /* Break long words to wrap */
  /*overflow-wrap: break-word; /* Ensure proper word wrapping */
}

::v-deep(thead th:nth-child(2)),
::v-deep(tbody td:nth-child(2)) {
  width: 800px !important; /* Set fixed width */
  max-width: 800px !important; /* Prevent expansion */
  white-space: normal; /* Allow text wrapping */
  /*word-wrap: break-word; /* Break long words to wrap */
  /*overflow-wrap: break-word; /* Ensure proper word wrapping */
}

::v-deep(thead th:nth-child(3)),
::v-deep(tbody td:nth-child(3)) {
  width: 150px !important; /* Set fixed width */
  max-width: 150px !important; /* Prevent expansion */
  white-space: normal; /* Allow text wrapping */
  /*word-wrap: break-word; /* Break long words to wrap */
  /*overflow-wrap: break-word; /* Ensure proper word wrapping */
}

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
/* .styled-table ::v-deep(tbody tr td), */
/* .styled-table ::v-deep(thead tr th) { */
/*text-indent: 32px; /* Indent text on the left */
/*position: relative; /* Make sure the pseudo-element aligns properly */
/* } */

/* Add indentation for the right side using a pseudo-element */
/* .styled-table ::v-deep(tbody tr td::after), */
/* .styled-table ::v-deep(thead tr th::after) { */
/* content: ''; Empty content for pseudo-element */
/* display: block; */
/* width: 32px; Create space on the right */
/* position: absolute; */
/* right: 0; */
/* height: 100%; */
/* } */
</style>
