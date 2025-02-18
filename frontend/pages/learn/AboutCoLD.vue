<template>
  <div>
    <!-- Carousel Section -->
    <!-- <div class="carousel-wrapper relative w-full overflow-hidden mt-6 mb-16">
      <UCarousel
        :items="items"
        :ui="{ item: 'basis-full' }"
        :prev-button="{
          icon: 'i-material-symbols:arrow-left-alt',
          class: 'custom-button custom-prev-button',
          size: '32px',
        }"
        :next-button="{
          icon: 'i-material-symbols:arrow-right-alt',
          class: 'custom-button custom-next-button',
          size: '32px',
        }"
        arrows
        indicators
      >
        <template v-slot="{ item }">
          <component :is="item" />
        </template> -->

    <!-- Custom Indicator Slot -->
    <!-- <template #indicator="{ onClick, index, active }">
          <button
            @click="onClick(index)"
            class="h-2 w-2 rounded-full"
            :class="{
              'bg-cold-night': active,
              'bg-cold-night-alpha-25': !active,
            }"
          ></button>
        </template>
      </UCarousel>
    </div> -->

    <!-- Copy Section -->
    <div class="copy" v-html="htmlContent"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { marked } from 'marked' // Import the Markdown parser
//import AboutRepo from './slider/AboutRepo.vue'
//import AboutCommunity from './slider/AboutCommunity.vue'
//import AboutOpenResearch from './slider/AboutOpenResearch.vue'

const content = ref('') // Reactive variable for storing the file content
const htmlContent = ref('') // Store parsed HTML content

//const items = [AboutRepo, AboutCommunity, AboutOpenResearch]

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
