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
      <div v-if="searchText">
        <!-- <p>Search Query: {{ searchText }}</p> -->
      </div>
      <div v-if="category">Category: {{ category }}</div>
      <div v-if="definition">{{ definition }}</div>
      <div v-else>
        <p>No matching definition found yet.</p>
      </div>
    </UCard>
  </UContainer>
</template>

<script>
export default {
  props: {
    searchText: {
      type: String,
      required: true,
    },
    searchPerformed: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      category: null, // Will be dynamically set based on searchText
      definition: null,
    }
  },
  mounted() {
    console.log('HelperChatbot mounted') // Add this log to check if HelperChatbot is being rendered
  },
  watch: {
    // Watch for changes in searchPerformed and trigger classifyQuery when true
    searchPerformed(newVal) {
      console.log('searchPerformed changed in HelperChatbot:', newVal)
      if (newVal) {
        console.log('searchPerformed is true, calling classifyQuery')
        this.classifyQuery(this.searchText) // Only run this when searchPerformed is true
      }
    },
  },
  methods: {
    async classifyQuery(query) {
      console.log('Classifying query:', query) // Debug log
      try {
        // Step 1: Call classify_query API to classify the search query
        const response = await fetch(
          'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/classify_query',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }),
          }
        )

        const category = await response.text() // Category returned from API
        console.log('Category received:', category) // Debug log
        this.category = category

        // Process the category to fetch relevant data
        this.processCategory()
      } catch (error) {
        console.error('Error classifying query:', error)
      }
    },
    processCategory() {
      if (!this.category) {
        console.error('Category not set.')
        return
      }

      // Simulate processing the category and fetching the definition
      this.definition = `Definition for ${this.category}`
      console.log('Definition set:', this.definition) // Debug log

      // Step 2: Split the category into the term and table
      const term = this.category.split(' (')[0]
      const tableType = this.category.match(/\(([^)]+)\)/)

      if (!tableType) {
        console.error('Invalid category format.')
        return
      }

      const type = tableType[1]
      let table = ''

      if (type === 'concept') {
        table = 'Concepts'
      } else if (type === 'principle') {
        table = 'HCCH Principles themes'
      }

      // Step 3: Make the API call with the term and table
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

        // Step 4: Find the entry with the appropriate matching key
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
      console.log(term, table)
    },
  },
}
</script>
