<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <UCard class="cold-ucard">
        <div
          class="copy main-content prose -space-y-10 flex flex-col gap-12 px-6 w-full"
          v-html="htmlContent"
        ></div>
      </UCard>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
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
    // Return false to use the default renderer for other headings
    return false
  },
}

// Extend marked with the custom renderer
marked.use({ renderer })

const content = ref('') // Raw Markdown content
const htmlContent = ref('') // Parsed HTML content

onMounted(async () => {
  try {
    const response = await fetch('/temp_glossary.txt')
    if (response.ok) {
      content.value = await response.text()
      htmlContent.value = marked.parse(content.value) // Parse Markdown with custom headings
      await nextTick()
      scrollToAnchor()
    } else {
      console.error('Failed to load text:', response.statusText)
    }
  } catch (error) {
    console.error('Error loading text:', error)
  }
})

// Scroll to the anchor link if it exists in the URL
function scrollToAnchor() {
  const anchor = window.location.hash
  if (anchor) {
    const targetElement = document.querySelector(anchor)
    if (targetElement) {
      targetElement.scrollIntoView({ behavior: 'smooth' })
    }
  }
}
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

::v-deep(h2) {
  /* margin-left: -82px !important; */
  margin-top: 24px !important;
}
</style>
