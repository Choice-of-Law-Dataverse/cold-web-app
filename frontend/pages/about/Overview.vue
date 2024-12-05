<template>
  <div class="carousel-wrapper">
    <UCarousel
      :items="items"
      :ui="{ item: 'basis-full' }"
      :prev-button="{
        icon: 'i-material-symbols:arrow-left-alt',
        class: 'custom-button custom-prev-button',
        size: '32px',
      }"
      :next-button="{
        color: 'gray',
        icon: 'i-material-symbols:arrow-right-alt',
        class: 'custom-button custom-next-button',
        size: '32px',
      }"
      arrows
      indicators
    >
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
::v-deep(.custom-button) {
  background: none !important; /* Remove background */
  border: none !important; /* Remove border */
  box-shadow: none !important; /* Remove any shadow */
  color: var(--color-cold-purple) !important; /* Set the icon color */
  font-size: 32px; /* Increase the icon size */
}

::v-deep(.custom-prev-button) {
  left: -54px;
}

::v-deep(.custom-next-button) {
  right: -54px;
}

.carousel-wrapper {
  width: 150%;
  margin-left: 140%; /* Push the left edge by 50% of the parent's width */
  transform: translateX(-75%); /* Pull back by 50% of the wrapper's width */
  margin-top: 24px;
  margin-bottom: 60px;
}
</style>
