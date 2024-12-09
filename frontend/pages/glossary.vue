<template>
  <div class="container">
    <div class="col-span-12">
      <UCard class="cold-ucard">
        <div class="main-content-grid">
          <div class="grid-item">
            <!-- Rendered HTML content -->
            <div class="copy" v-html="htmlContent"></div>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { marked } from 'marked'

// Custom renderer for marked
const renderer = {
  heading(token) {
    if (token.depth === 2) {
      const slug = token.text
        .toLowerCase()
        .trim()
        .replace(/\s+/g, '-') // Replace spaces with hyphens
        .replace(/[^\w-]/g, '') // Remove special characters

      return `<h2 id="${slug}">
                <a href="#${slug}" class="anchor-link"></a>
                ${token.text}
              </h2>`
    }
    return false // Use default renderer for other headings
  },
}

// Extend marked with the custom renderer
marked.use({ renderer })

const content = ref('') // Store raw Markdown content
const htmlContent = ref('') // Store parsed HTML content

onMounted(async () => {
  try {
    const response = await fetch('/temp_glossary.txt') // Fetch the Markdown file
    if (response.ok) {
      content.value = await response.text() // Store raw Markdown
      htmlContent.value = marked.parse(content.value) // Parse Markdown to HTML
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
}

h2 {
  position: relative;
  margin-top: 48px;
}

.anchor-link {
  text-decoration: none;
  color: #888; /* Light grey for the anchor */
  margin-right: 8px;
  font-size: 0.8em;
}

.anchor-link:hover {
  color: #333; /* Darker color on hover */
}
</style>
