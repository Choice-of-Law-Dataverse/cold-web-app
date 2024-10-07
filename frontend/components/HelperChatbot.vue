<template>
  <UContainer
    style="
      margin-top: 50px;
      width: 80%;
      max-width: 1200px;
      margin-left: auto;
      margin-right: auto;
    "
  >
    <h2>Helper Chatbot Response</h2>
    <UCard
      :style="{ backgroundColor: '#f5f5f5', boxShadow: 'none', border: 'none' }"
    >
      <div v-if="definition">{{ definition }}</div>
      <div v-else>
        <p>No matching definition found yet.</p>
      </div>
    </UCard>
  </UContainer>
</template>

<script>
export default {
  data() {
    return {
      category: 'Dépeçage (concept)', // Example category, this should be passed dynamically
      definition: null,
    }
  },
  mounted() {
    this.processCategory()
  },
  methods: {
    processCategory() {
      // Step 1: Split the category into the term and the table
      const term = this.category.split(' (')[0]
      const tableType = this.category.match(/\(([^)]+)\)/)[1]

      let table = ''

      if (tableType === 'concept') {
        table = 'Concepts'
      } else if (tableType === 'principle') {
        table = 'HCCH Principles themes'
      }

      // Step 2: Make the API call with the table
      this.fetchData(term, table)
    },

    async fetchData(term, table) {
      try {
        const response = await fetch(
          'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/full_table',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ table: table }),
          }
        )

        const data = await response.json()

        // Step 3: Find the entry with the appropriate matching key
        let matchedEntry
        if (table === 'HCCH Principles themes') {
          // For "HCCH Principles themes", match against the "Theme" key
          matchedEntry = data.find(
            (entry) => entry.Theme && entry.Theme.includes(term)
          )
        } else {
          // For other tables, match against the "Keywords" key
          matchedEntry = data.find(
            (entry) => entry.Keywords && entry.Keywords.includes(term)
          )
        }

        if (matchedEntry) {
          // Step 4: If table is "HCCH Principles themes", get "Full text" key, otherwise get "Definition"
          if (table === 'HCCH Principles themes') {
            this.definition =
              matchedEntry['Full text'] || 'No full text found for this term.'
          } else {
            this.definition =
              matchedEntry.Definition || 'No definition found for this term.'
          }
        } else {
          this.definition = 'No matching entry found for this term.'
        }
      } catch (error) {
        console.error('Error fetching data:', error)
      }
    },
  },
}
</script>
