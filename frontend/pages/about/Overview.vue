<template>
  <div class="carousel-wrapper">
    <UCarousel :items="items" :ui="{ item: 'basis-full' }" arrows indicators>
      <template v-slot="{ item }">
        <component :is="item" />
      </template>
    </UCarousel>
  </div>
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
.carousel-wrapper {
  width: 150%; /* Set the carousel width to 80% of the parent container */
}
</style>
