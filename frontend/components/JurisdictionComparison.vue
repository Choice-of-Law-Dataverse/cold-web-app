<template>
  <div class="col-span-12">
    <!-- Filter Dropdown -->
    <div class="flex items-center space-x-4 mb-4">
      <USelectMenu
        v-model="selectedTheme"
        :options="themeOptions"
        placeholder="Filter by Theme"
        class="w-40"
      />
      <UButton @click="resetFilters" size="sm">Reset</UButton>
    </div>
    <UCard class="cold-ucard">
      <UTable
        v-if="!loading"
        class="styled-table"
        :rows="filteredRows"
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
import { ref, watch, onMounted, computed } from 'vue'

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

// Dropdown options for themes
const themeOptions = ref([
  { label: 'Preamble', value: 'Preamble' },
  { label: 'Arbitration', value: 'Arbitration' },
  { label: 'Absence of choice', value: 'Absence of choice' },
  { label: 'Party autonomy', value: 'Party autonomy' },
  { label: 'Freedom of choice', value: 'Freedom of choice' },
  { label: 'Partial choice', value: 'Partial choice' },
  { label: 'Dépeçage', value: 'Dépeçage' },
  { label: 'Rules of law', value: 'Rules of law' },
  { label: 'Express and tacit choice', value: 'Express and tacit choice' },
  { label: 'Mandatory rules', value: 'Mandatory rules' },
  { label: 'Public policy', value: 'Public policy' },
  { label: 'Scope of the Principles', value: 'Scope of the Principles' },
  { label: 'Universal application', value: 'Universal application' },
  {
    label: 'Role of international instruments',
    value: 'Role of international instruments',
  },
  {
    label:
      'Consent and material validity; choice of law in the battle of forms',
    value:
      'Consent and material validity; choice of law in the battle of forms',
  },
  { label: 'Formal validity', value: 'Formal validity' },
  { label: 'Renvoi', value: 'Renvoi' },
  {
    label: 'Scope of the law applicable to the contract',
    value: 'Scope of the law applicable to the contract',
  },
  { label: 'Set-off', value: 'Set-off' },
  { label: 'Habitual residence', value: 'Habitual residence' },
  {
    label: 'Interpretation and uniformity of application',
    value: 'Interpretation and uniformity of application',
  },
  {
    label: 'Entry into force and application in time',
    value: 'Entry into force and application in time',
  },
])

// Selected theme for filtering
const selectedTheme = ref(null)

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

// Desired order for the questions
const questionOrder = [
  'Is there a codification on choice of law or are there similar established rules?',
  'Are these rules part of a private international law instrument?',
  'Are these rules a consequence of a recent law reform?',
  'If a codification of private international law exists, is any revision of these rules under discussion?',
  'Could the HCCH Principles be expected to play a model role in this regard?',
  'If an implementation is not under discussion, could the HCCH Principles be expected to play any role in interpreting rules of private international law?',
  'If an implementation is not under discussion, could the HCCH Principles be expected to play any role in supplementing rules of private international law?',
  'If an implementation is not under discussion, could the HCCH Principles be expected to play any role in developing rules of private international law?',
  'Do the courts have the authority to refer to the HCCH Principles as persuasive authority?',
  'Is the principle of party autonomy in respect of choice of law in international commercial contracts widely accepted in your jurisdiction?',
  'Are the parties to an international commercial contract thus allowed to choose the law applicable to their contract?',
  'Are the parties allowed to choose different laws for different parts or aspects of the contract? ',
  'Are the parties allowed to choose the applicable law with respect to only one part or aspect of their contract?',
  'Are the parties allowed to make or modify a choice of law at any time?',
  'May an internal modification of the agreement on the applicable law after the conclusion of the contract be valid even if a specific form is requested for the original choice?',
  'May a choice of law or modification made after the conclusion of the contract have an impact on the rights of third parties?',
  'Is a connection required between the chosen law and the parties or their transaction? ',
  'Are the parties prevented from choosing the law of a third country with which there is no connection (a “neutral law”)?',
  'Are there any published cases in your jurisdiction in which an agreement by the parties on the applicable law was not respected for lack of such a connection? ',
  'Are the parties allowed to choose non-State law (“rules of law”) to govern their contract?',
  'Are there any particular requirements or restrictions with regard to the eligible rules of law?',
  'Are the parties allowed to incorporate rules of law into their contract by way of reference? ',
  'Are there any requirements for the effective incorporation of such rules?',
  'Does your jurisdiction require a choice of law to be made expressly?',
  'Can a choice of law be made tacitly?',
  'Is tacit choice of law clearly distinguished from the position where there is no choice of law?',
  'Are clear criteria employed to examine whether there is a tacit choice of law?',
  'May a tacit choice of law be deduced from the provisions of the contract?',
  'May a tacit choice of law be deduced from the reference to legal provisions?',
  'May a tacit choice of law be deduced from the reference to institutions of a particular jurisdiction?',
  'May a tacit choice of law be deduced from the circumstances?',
  'May a tacit choice of law be deduced from other criteria?',
  'Does a choice of court or arbitral tribunal automatically indicate a tacit choice of law? ',
  'May a choice of court or arbitral tribunal be taken into account as one of the relevant factors in this regard?',
  'May the parties choose non-State law tacitly?',
  'Do the courts in your jurisdiction readily admit the existence of a tacit choice of law?',
  'Do legal authorities (doctrine) consider the existence of tacit agreements?',
  'Is there a definition of “overriding mandatory provision” or a similar concept (for instance, a rule of direct or immediate application; an internationally mandatory rule) in your jurisdiction?',
  'Do the courts in your jurisdiction apply overriding mandatory provisions of the law of the forum under certain circumstances? ',
  'If the courts in your jurisdiction sometimes apply overriding mandatory provisions of the law of the forum, under which circumstances will this be the case?',
  'Do the courts apply overriding mandatory provisions of other jurisdictions?',
  'Do the courts take into account overriding mandatory provisions of other jurisdictions?',
  'Is there a definition for “public policy”? ',
  'Is there a particular notion or understanding of public policy with regard to the field of commercial law?',
  'Do the courts exclude the application of a provision of the law chosen by the parties if (the result of) such application would be manifestly incompatible with the public policy of the forum?',
  'Do the courts apply or take into account the public policy of a State whose law would be applicable in the absence of a choice of law?',
  'Do arbitral tribunals have the authority to apply the HCCH Principles?',
  'Do arbitral tribunals apply or take into account overriding mandatory provisions or the public policy of a law other than the law chosen by the parties? ',
  'Does the codification on arbitration, if any, include conflict of laws rules?',
  'Is any revision of the lex arbitri under discussion?',
  'Is there a legal framework to tackle the issue of absence of choice?',
  'Do clear connecting factors exist?',
  'Which are the most common connecting factors?',
  'Among these, what is the most frequently used connecting factor?',
  'Is this connecting factor suitable to be considered a general default rule?',
  'Are you aware of any recent arbitral award dealing with this issue?',
  'Is a future version of the HCCH Principles covering the law applicable in the absence of a choice of law by the parties desirable?',
  'Is further guidance on applicable law in international contracts providing protection to weaker parties necessary?',
  'Are there other topics that should be considered for further guidance or revision of the HCCH principles?',
  'Should the HCCH Principles be incorporated into a new HCCH instrument?',
]

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

    // Sort rows based on desired order
    rows.value = data.sort((a, b) => {
      const indexA = questionOrder.indexOf(a.Questions)
      const indexB = questionOrder.indexOf(b.Questions)
      return indexA - indexB
    })
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
