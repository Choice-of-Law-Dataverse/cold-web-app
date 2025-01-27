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
    <!-- <h2>Helper Chatbot Response</h2> -->
    <UCard
      :style="{
        backgroundColor: 'rgb(250, 250, 250)',
      }"
    >
      <div v-if="definition">
        <!-- Robot icon with font-size large and dark grey color -->
        <UIcon
          name="i-material-symbols:smart-toy-outline"
          :style="{ fontSize: 'large', color: 'rgb(60, 60, 60)' }"
        />

        <!-- SMS icon with font-size large, margin-bottom 6px, and dark grey color -->
        <UIcon
          name="i-material-symbols:sms-outline"
          :style="{
            fontSize: 'large',
            marginBottom: '6px',
            color: 'rgb(60, 60, 60)',
          }"
        />
      </div>

      <div v-if="definition">
        {{ definition }}
      </div>

      <div v-if="category">
        <small
          ><br />
          Category: {{ category }}</small
        >
      </div>
      <div v-else>
        <p>No matching definition found yet.</p>
      </div>
    </UCard>
  </UContainer>
</template>

<script>
const config = useRuntimeConfig()

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
  watch: {
    // Watch for changes in searchPerformed and trigger classifyQuery when true
    searchPerformed(newVal) {
      if (newVal) {
        this.classifyQuery(this.searchText) // Only run this when searchPerformed is true
      }
    },
  },
  methods: {
    async classifyQuery(query) {
      try {
        // Step 1: Call classify_query API to classify the search query
        const response = await fetch(
          `${config.public.apiBaseUrl}/classify_query`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
          }
        )

        const category = await response.text() // Category returned from API
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
        const response = await fetch(`${config.public.apiBaseUrl}/full_table`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ table }),
        })

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
    },
  },
}
</script>
