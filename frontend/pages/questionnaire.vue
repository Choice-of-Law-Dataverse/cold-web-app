<template>
  <div class="container">
    <div class="col-span-12">
      <UCard class="cold-ucard">
        <div class="main-content-grid">
          <div class="grid-item">
            <div class="copy" v-html="htmlContent"></div>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { marked } from 'marked' // Import the Markdown parser

marked.setOptions({
  //gfm: true, // Enable GitHub Flavored Markdown
})

const content = ref('') // Reactive variable for storing the file content
const htmlContent = ref('') // Store parsed HTML content

onMounted(async () => {
  try {
    const response = await fetch('/temp_questionnaire.txt') // Fetch the Markdown file
    if (response.ok) {
      content.value = await response.text() // Store raw Markdown
      htmlContent.value = marked(content.value) // Convert Markdown to HTML
    } else {
      console.error('Failed to load text:', response.statusText)
    }
  } catch (error) {
    console.error('Error loading text:', error)
  }
})
</script>

<style scoped>
::v-deep(ol) {
  list-style: decimal !important; /* Ensure numbers are displayed */
  /*margin-left: 14px; /* Add some left padding if needed */
}

::v-deep(ol ol) {
  /*list-style: decimal !important; /* Sub-numbering style (optional) */
  margin-left: 20px !important; /* Further indent nested lists */
}

::v-deep(ol ol ol) {
  /*list-style: lower-roman !important; /* Third-level numbering style (optional) */
  margin-left: 20px !important;
}

.main-content-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr)); /* 12-column layout */
  column-gap: var(--gutter-width); /* Gutter space between columns */
  padding: 32px; /* Optional padding to match the card's interior padding */
}

.grid-item {
  grid-column: 1 / span 6; /* Start in the 1st column, span across 6 columns */
  margin-bottom: 48px; /* Space between items */
}

::v-deep(h2) {
  margin-top: 20px;
}
</style>
