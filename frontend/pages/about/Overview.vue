<template>
  <UCarousel
    :items="items"
    :ui="{ item: 'basis-full' }"
    class="rounded-lg overflow-hidden"
    arrows
    indicators
  >
    <template v-slot="{ item }">
      <component :is="item" />
    </template>
  </UCarousel>
  <div class="copy" v-html="htmlContent"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { marked } from 'marked' // Import the Markdown parser
import AboutRepo from './slider/AboutRepo.vue'
import AboutCommunity from './slider/AboutCommunity.vue'
import AboutOpenResearch from './slider/AboutOpenResearch.vue'

const content = ref('') // Reactive variable for storing the file content
const htmlContent = ref('') // Store parsed HTML content

const items = [AboutRepo, AboutCommunity, AboutOpenResearch]

onMounted(async () => {
  try {
    const response = await fetch('/temp_overview.txt') // Fetch the Markdown file
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
</style>
