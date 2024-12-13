<template>
  <div class="col-span-12">
    <UCard class="cold-ucard">
      <!-- Centered Jurisdiction Name and Compare Dropdown -->
      <div class="comparison-title flex items-center justify-center mb-4">
        <div class="result-value-medium">
          Questions for {{ props.jurisdiction }} and
        </div>
        <USelectMenu
          searchable
          searchable-placeholder="Search a Jurisdiction..."
          v-model="selectedJurisdiction"
          :options="jurisdictionOptions"
          placeholder="Select Jurisdiction"
          class="w-72 cold-uselectmenu"
          size="xl"
          style="margin-top: -16px; margin-left: 4px"
          :popper="{ offsetDistance: 0 }"
          :uiMenu="{
            base: 'rounded-none text-base', // Dropdown container styles
          }"
        />
      </div>

      <!-- Filter and MatchSummary -->
      <div class="main-content-grid">
        <!-- Left-aligned USelectMenu -->
        <div class="filter-wrapper">
          <USelectMenu
            searchable
            v-model="selectedTheme"
            :options="themeOptions"
            placeholder="Filter by Theme"
            class="cold-uselectmenu"
            size="sm"
          />
          <UButton
            v-if="selectedTheme"
            @click="resetFilters"
            size="sm"
            variant="link"
            class="suggestion-button"
          >
            Reset
          </UButton>
        </div>

        <!-- Right-aligned MatchSummary -->
        <div v-if="selectedJurisdiction" class="match-summary">
          <MatchSummary :counts="matchCounts" />
        </div>
      </div>

      <hr style="margin-top: 8px" />

      <!-- Table -->
      <ComparisonTable
        :rows="filteredRows"
        :columns="columns"
        :loading="loading"
      />
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import MatchSummary from './MatchSummary.vue'
import ComparisonTable from './ComparisonTable.vue'

const props = defineProps({
  jurisdiction: {
    type: String,
    required: true,
  },
  compareJurisdiction: {
    type: String,
    default: null,
  },
})

const router = useRouter() // Access the router to update the query parameters
const loading = ref(true)
const rows = ref([])
const jurisdictionOptions = ref([]) // Options for the dropdown
const selectedJurisdiction = ref(null) // Selected jurisdiction for comparison
const selectedTheme = ref(null) // Selected theme for filtering
const columns = ref([
  { key: 'Themes', label: 'Theme', class: 'label' },
  { key: 'Questions', label: 'Question', class: 'label' },
  { key: 'Answer', label: props.jurisdiction || 'Answer', class: 'label' },
])

// Computed filtered rows
const filteredRows = computed(() => {
  if (!selectedTheme.value) {
    return rows.value
  }

  return rows.value.filter((row) =>
    row.Themes.includes(selectedTheme.value.value)
  )
})

// Reset filter button action
const resetFilters = () => {
  selectedTheme.value = null
}

// Dropdown options for themes
import themeOptionsData from './assets/themeOptions.json'
const themeOptions = ref(themeOptionsData)

// Desired order for the questions
import questionOrderData from './assets/questionOrder.json'
const questionOrder = questionOrderData

async function fetchData(url, payload) {
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!response.ok) throw new Error('Fetch failed')
    return await response.json()
  } catch (error) {
    console.error('Error fetching data:', error)
    return []
  }
}

async function fetchFilteredTableData(filters) {
  const payload = {
    table: 'Answers',
    filters: filters,
  }

  try {
    const data = await fetchData(
      'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/full_table',
      payload
    )
    return data.map((item) => ({
      ...item,
      ID: item.ID,
    }))
  } catch (error) {
    console.error('Error fetching filtered table data:', error)
    return [] // Fallback to empty data
  }
}

async function fetchTableData(jurisdiction) {
  loading.value = true
  try {
    const data = await fetchFilteredTableData([
      { column: 'Name (from Jurisdiction)', value: jurisdiction },
    ])

    rows.value = data.sort(
      (a, b) =>
        questionOrder.indexOf(a.Questions) - questionOrder.indexOf(b.Questions)
    )
  } finally {
    loading.value = false
  }
}

// Fetch jurisdictions from the text file
async function fetchJurisdictions() {
  try {
    const response = await fetch('/temp_jurisdictions.txt')
    if (!response.ok) throw new Error('Failed to load jurisdictions')

    const text = await response.text()
    jurisdictionOptions.value = text
      .split('\n')
      .map((country) => country.trim())
      .filter(Boolean)
      .map((country) => ({ label: country, value: country }))
  } catch (error) {
    console.error('Error fetching jurisdictions:', error)
    jurisdictionOptions.value = [] // Fallback to an empty list
  }
}

onMounted(() => {
  fetchJurisdictions().then(() => {
    if (props.jurisdiction) {
      fetchTableData(props.jurisdiction)
    }

    const compareQuery = router.currentRoute.value.query.c
    if (compareQuery) {
      const originalValue = compareQuery.replace(/_/g, ' ') // Transform '_' back to spaces
      const option = jurisdictionOptions.value.find(
        (opt) => opt.value === originalValue
      )
      if (option) {
        selectedJurisdiction.value = option // Update dropdown
        updateComparison(option) // Trigger table update
      }
    }
  })
})

// Add selected jurisdiction as a column
async function updateComparison(jurisdiction) {
  if (!jurisdiction) return

  loading.value = true
  try {
    const jurisdictionData = await fetchFilteredTableData([
      { column: 'Name (from Jurisdiction)', value: jurisdiction.value },
    ])

    updateColumns(jurisdiction)
    updateRows(jurisdictionData, jurisdiction)
  } finally {
    loading.value = false
  }
}

function updateColumns(jurisdiction) {
  const secondColumnKey = `Answer_${jurisdiction.value}`
  columns.value = [
    { key: 'Themes', label: 'Theme', class: 'label' },
    { key: 'Questions', label: 'Question', class: 'label' },
    { key: 'Answer', label: props.jurisdiction || 'Answer', class: 'label' },
    { key: secondColumnKey, label: jurisdiction.label, class: 'label' },
    { key: 'Match', label: '', class: 'match-column' },
  ]
}

function updateRows(jurisdictionData, jurisdiction) {
  const secondColumnKey = `Answer_${jurisdiction.value}`
  rows.value = rows.value.map((row) => {
    const match = jurisdictionData.find(
      (item) => item.Questions === row.Questions
    )
    return {
      ...row,
      [secondColumnKey]: match?.Answer || 'N/A',
      [`${secondColumnKey}_ID`]: match?.ID || null,
      Match: { answer1: row.Answer, answer2: match?.Answer || 'N/A' },
    }
  })
}

watch(
  () => [selectedJurisdiction.value, router.currentRoute.value.query.c],
  ([newJurisdiction, newCompare]) => {
    if (newJurisdiction) {
      updateRouterQuery(newJurisdiction.value)
      updateComparison(newJurisdiction)
    }
    if (newCompare) {
      syncCompareJurisdiction(newCompare)
    }
  }
)

function updateRouterQuery(jurisdiction) {
  router.replace({
    query: {
      ...router.currentRoute.value.query,
      c: jurisdiction.replace(/ /g, '_'),
    },
  })
}

function syncCompareJurisdiction(compare) {
  const originalValue = compare.replace(/_/g, ' ')
  const option = jurisdictionOptions.value.find(
    (opt) => opt.value === originalValue
  )
  if (option) selectedJurisdiction.value = option
}

// Computed property to calculate match counts dynamically
const matchCounts = computed(() => {
  return filteredRows.value.reduce(
    (counts, row) => {
      const match = row.Match
      if (match) {
        counts[match] = (counts[match] || 0) + 1
      }
      return counts
    },
    { green: 0, red: 0, 'red-x': 0, gray: 0 }
  )
})
</script>

<style scoped>
::v-deep(.z-20.group.w-full [role='option']) {
  line-height: 2 !important; /* Make the line height larger */
}

::v-deep(.cold-uselectmenu span.block.truncate) {
  color: var(--color-cold-night);
}

.comparison-title {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
  padding-top: 55px;
}

.circle-placeholder {
  width: 62px;
  height: 62px;
  border-radius: 50%;
  border: 8px solid var(--color-cold-gray);
  background-color: transparent;
  margin-left: 24px;
  margin-right: 24px;
}

.result-value-large {
  margin-bottom: -4px !important;
}

.suggestion-button {
  color: var(--color-cold-purple) !important;
  font-size: 14px !important;
}

.main-content-grid {
  display: flex; /* Use flexbox for layout */
  justify-content: space-between; /* Space between left and right sections */
  align-items: center; /* Vertically align items */
  margin-bottom: 16px; /* Adjust spacing below */
}

.filter-wrapper {
  margin-left: 32px;
  margin-bottom: 6px;
  display: flex; /* Group the dropdown and reset button */
  align-items: center;
  gap: 8px; /* Space between the dropdown and reset button */
}

.match-summary {
  margin-left: auto; /* Push the MatchSummary component to the far right */
  margin-right: 24px;
  margin-bottom: 6px; /* Vertical alignment with Filter by Theme */
  text-align: right;
}

::v-deep(thead th:nth-child(1)),
::v-deep(tbody td:nth-child(1)) {
  width: 200px !important; /* Set fixed width */
  max-width: 200px !important; /* Prevent expansion */
  white-space: normal; /* Allow text wrapping */
}

::v-deep(thead th:nth-child(2)),
::v-deep(tbody td:nth-child(2)) {
  width: 800px !important; /* Set fixed width */
  max-width: 800px !important; /* Prevent expansion */
  white-space: normal; /* Allow text wrapping */
}

::v-deep(thead th:nth-child(3)),
::v-deep(tbody td:nth-child(3)) {
  width: 150px !important; /* Set fixed width */
  max-width: 150px !important; /* Prevent expansion */
  white-space: normal; /* Allow text wrapping */
}

::v-deep(thead th:nth-child(4)),
::v-deep(tbody td:nth-child(4)) {
  width: 150px !important; /* Set fixed width */
  max-width: 150px !important; /* Prevent expansion */
  white-space: normal; /* Allow text wrapping */
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
</style>
