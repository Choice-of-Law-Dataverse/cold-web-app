<template>
  <div class="copy" v-html="htmlContent"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { marked } from 'marked' // Import the Markdown parser

const content = ref('') // Reactive variable for storing the file content
const htmlContent = ref('') // Store parsed HTML content

onMounted(async () => {
  try {
    const response = await fetch('/temp_open_educational_resources.txt') // Fetch the Markdown file
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
.main-content-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr)); /* 12-column layout */
  column-gap: var(--gutter-width); /* Gutter space between columns */
  padding: 32px; /* Optional padding to match the card's interior padding */
}

.grid-item {
  grid-column: 1 / span 6; /* Start in the 1st column, span across 6 columns */
  margin-bottom: 48px; /* Space between each key-value pair */
}

::v-deep(h2) {
  margin-top: 60px;
}
</style>
