<template>
  <div class="col-span-12">
    <UCard class="cold-ucard relative">
      <!-- Help/Cancel Icon -->
      <div class="absolute top-5 right-5">
        <Icon
          v-if="!showInfo"
          name="i-material-symbols:help-outline"
          size="24"
          style="color: var(--color-cold-purple)"
          class="cursor-pointer"
          @click="toggleInfo"
        />
        <Icon
          v-else
          name="i-material-symbols:cancel-outline"
          size="24"
          style="color: var(--color-cold-purple)"
          class="cursor-pointer"
          @click="toggleInfo"
        />
      </div>

      <!-- Conditional Rendering -->
      <div v-if="showInfo">
        <!-- JurisdictionComparisonInfo Component -->
        <JurisdictionComparisonInfo />
      </div>
      <div v-else>
        <!-- Centered Jurisdiction Name and Compare Dropdown -->
        <div
          class="comparison-title flex flex-col md:flex-row items-center justify-center gap-4 px-6 mb-4 text-center md:text-left"
        >
          <div class="result-value-medium">
            Questions for {{ props.jurisdiction }} and
          </div>
          <JurisdictionSelectMenu
            v-model="selectedJurisdiction"
            :countries="jurisdictionOptions"
            @countrySelected="updateComparison"
            class="w-full md:w-72 cold-uselectmenu"
          />
        </div>

        <!-- Filter and MatchSummary -->
        <div
          class="main-content-grid flex flex-col sm:flex-row items-center sm:items-start justify-between gap-4 !px-4 !sm:px-8"
        >
          <!-- Left-aligned USelectMenu -->
          <div
            class="filter-wrapper flex flex-col items-center sm:flex-row sm:items-center justify-center w-full sm:w-auto"
          >
            <USelectMenu
              searchable
              v-model="selectedTheme"
              :options="themeOptions"
              placeholder="Filter by Theme"
              class="cold-uselectmenu w-full max-w-full sm:w-auto text-center"
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
          <div
            v-if="selectedJurisdiction"
            class="match-summary flex justify-center sm:justify-start w-full sm:w-auto"
          >
            <MatchSummary :counts="matchCounts" />
          </div>
        </div>
      </div>

      <hr style="margin-top: 8px" />

      <!-- Table Always Visible -->
      <ComparisonTable
        :rows="filteredRows"
        :columns="columns"
        :computeMatchStatus="computeMatchStatus"
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
import JurisdictionSelectMenu from './JurisdictionSelectMenu.vue'

const props = defineProps({
  jurisdiction: {
    type: String,
    required: true,
  },
  compareJurisdiction: {
    type: String,
    default: null,
  },
  isInternational: {
    type: Boolean,
    default: false,
  },
  cardType: {
    type: String,
    default: '', // use an empty string or a proper default value
  },
})

const router = useRouter() // Access the router to update the query parameters
const loading = ref(true)
const rows = ref([])
const jurisdictionOptions = ref([]) // Options for the dropdown
const selectedJurisdiction = ref(null) // Selected jurisdiction for comparison
const selectedTheme = ref(null) // Selected theme for filtering
const showInfo = ref(false) // Reactive state to toggle the JurisdictionComparisonInfo component
const columns = ref([
  { key: 'Themes', label: 'Theme', class: 'label' },
  { key: 'Question', label: 'Question', class: 'label' },
  { key: 'Answer', label: props.jurisdiction || 'Answer', class: 'label' },
])

const config = useRuntimeConfig()

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
import themeOptionsData from '../assets/themeOptions.json'
const themeOptions = ref(themeOptionsData)

// Desired order for the questions
import questionOrderData from '../assets/questionOrder.json'
const questionOrder = questionOrderData

// Function to toggle the state
function toggleInfo() {
  showInfo.value = !showInfo.value
}

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
    const response = await fetch(
      `${config.public.apiBaseUrl}/search/full_table`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      }
    )

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    const data = await response.json()

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
      { column: 'Jurisdictions', value: jurisdiction },
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
    const config = useRuntimeConfig() // Ensure config is accessible

    const jsonPayload = {
      table: 'Jurisdictions',
      filters: [],
    }

    const response = await fetch(
      `${config.public.apiBaseUrl}/search/full_table`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonPayload),
      }
    )

    if (!response.ok) throw new Error('Failed to load jurisdictions')

    const data = await response.json()

    // Filter out jurisdictions where "Irrelevant?" is explicitly true
    const relevantJurisdictions = data.filter(
      (entry) => entry['Irrelevant?'] === null
    )

    // Extract and format jurisdiction names
    let jurisdictionNames = relevantJurisdictions
      .map((entry) => entry.Name)
      .filter(Boolean)

    // Sort and format the list
    jurisdictionOptions.value = jurisdictionNames
      .sort((a, b) => a.localeCompare(b))
      .map((name) => ({ label: name, value: name })) // Ensure correct structure
  } catch (error) {
    console.error('Error fetching jurisdictions:', error)
    jurisdictionOptions.value = [] // Fallback to an empty list
  }
}

onMounted(async () => {
  await fetchJurisdictions() // Ensure jurisdictions are loaded first

  const compareQuery = router.currentRoute.value.query.c
  if (compareQuery) {
    await syncCompareJurisdiction(compareQuery) // Sync the dropdown
    const jurisdiction = selectedJurisdiction.value
    if (jurisdiction) {
      updateComparison(jurisdiction) // Update the table
    }
  }

  // If a primary jurisdiction is set via props, load its data
  if (props.jurisdiction) {
    fetchTableData(props.jurisdiction)
  }
})

// Add selected jurisdiction as a column
async function updateComparison(jurisdiction) {
  if (!jurisdiction) return

  loading.value = true
  try {
    const jurisdictionData = await fetchFilteredTableData([
      { column: 'Jurisdictions', value: jurisdiction.value },
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
    { key: 'Question', label: 'Question', class: 'label' },
    { key: 'Answer', label: props.jurisdiction || 'Answer', class: 'label' },
    { key: secondColumnKey, label: jurisdiction.label, class: 'label' },
    { key: 'Match', label: '', class: 'match-column' },
  ]
}

function updateRows(jurisdictionData, jurisdiction) {
  const secondColumnKey = `Answer_${jurisdiction.value}`
  rows.value = rows.value.map((row) => {
    const match = jurisdictionData.find(
      (item) => item.Question === row.Question
    )
    return {
      ...row,
      [secondColumnKey]: match?.Answer || 'N/A',
      [`${secondColumnKey}_ID`]: match?.ID || null,
      Match: { answer1: row.Answer, answer2: match?.Answer || 'N/A' },
    }
  })
}

// Watch when the user changes the selected jurisdiction
watch(selectedJurisdiction, (newJurisdiction) => {
  if (newJurisdiction) {
    updateRouterQuery(newJurisdiction.value) // Fetch ISO3 and update query
    updateComparison(newJurisdiction) // Fetch new comparison data
  }
})

// Watch for URL query updates to sync the dropdown
watch(
  () => router.currentRoute.value.query.c,
  async (newCompare) => {
    if (newCompare) {
      if (!jurisdictionOptions.value.length) {
        await fetchJurisdictions() // Ensure jurisdictions are loaded
      }
      await syncCompareJurisdiction(newCompare) // Sync dropdown
      const jurisdiction = selectedJurisdiction.value
      if (jurisdiction) {
        updateComparison(jurisdiction) // Update table data
      }
    }
  },
  { immediate: true }
)

async function updateRouterQuery(jurisdiction) {
  try {
    const response = await fetch(
      `https://restcountries.com/v3.1/name/${jurisdiction}?fields=cca3`
    )
    const data = await response.json()

    if (data && data[0] && data[0].cca3) {
      const isoCode = data[0].cca3.toLowerCase() // Convert ISO3 code to lowercase
      router.replace({
        query: {
          ...router.currentRoute.value.query,
          c: isoCode, // Update query with ISO3 code
        },
      })
    } else {
      console.error(`ISO3 code not found for jurisdiction: ${jurisdiction}`)
    }
  } catch (error) {
    console.error('Error fetching ISO3 code:', error)
  }
}

async function syncCompareJurisdiction(compare) {
  const isoCode = compare.toUpperCase() // Ensure ISO3 code is uppercase
  try {
    // Fetch full name using ISO3 code
    const response = await fetch(
      `https://restcountries.com/v3.1/alpha/${isoCode}?fields=name`
    )
    const data = await response.json()

    if (data && data.name?.common) {
      const fullName = data.name.common
      const option = jurisdictionOptions.value.find(
        (opt) => opt.value === fullName
      )
      if (option) {
        selectedJurisdiction.value = option // Update dropdown selection
      } else {
        console.warn(`Jurisdiction not found in dropdown for: ${fullName}`)
      }
    } else {
      console.error(`Full name not found for ISO3 code: ${compare}`)
    }
  } catch (error) {
    console.error('Error syncing compare jurisdiction:', error)
  }
}

// Computed property to calculate match counts dynamically
const matchCounts = computed(() => {
  return filteredRows.value.reduce(
    (counts, row) => {
      const match = row.Match
      if (match) {
        const status = computeMatchStatus(match.answer1, match.answer2)
        counts[status] = (counts[status] || 0) + 1
      }
      return counts
    },
    { green: 0, red: 0, 'red-x': 0, gray: 0 }
  )
})

function computeMatchStatus(answer1, answer2) {
  const grayCases = ['Unclear', 'Information is not available yet', 'No data']

  if (grayCases.includes(answer1) || grayCases.includes(answer2)) return 'gray'
  if (answer1 === answer2 && answer1 !== 'No') return 'green'
  if (answer1 === 'No' && answer2 === 'No') return 'red'
  if (
    (answer1 === 'Yes' && answer2 === 'No') ||
    (answer1 === 'No' && answer2 === 'Yes')
  )
    return 'red-x'

  return 'gray'
}
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

.filter-wrapper {
  /* margin-left: 32px; */
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
