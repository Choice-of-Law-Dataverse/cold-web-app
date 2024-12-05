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
/* Reset the counter for the top-level list */
::v-deep(ol) {
  counter-reset: list-counter; /* Initialize the counter */
  list-style: none; /* Remove the default numbering */
  margin-left: 0;
  padding-left: 0;
}

::v-deep(ol > li) {
  counter-increment: list-counter; /* Increment the counter for each list item */
}

::v-deep(ol > li::before) {
  content: counter(list-counter) '. '; /* Display the counter number */
  font-weight: bold;
}

::v-deep(ol ol) {
  counter-reset: sub-list-counter; /* Reset the sub-list counter */
  list-style: none; /* Remove the default numbering */
  margin-left: 20px; /* Indent for sub-lists */
}

::v-deep(ol ol > li) {
  counter-increment: sub-list-counter; /* Increment the sub-list counter */
}

::v-deep(ol ol > li::before) {
  content: counter(list-counter) '.' counter(sub-list-counter) '. '; /* Display hierarchical numbering */
  font-weight: bold;
}

::v-deep(ol ol ol) {
  counter-reset: sub-sub-list-counter; /* Reset the sub-sub-list counter */
  list-style: none; /* Remove the default numbering */
  margin-left: 20px; /* Indent for sub-sub-lists */
}

::v-deep(ol ol ol > li) {
  counter-increment: sub-sub-list-counter; /* Increment the sub-sub-list counter */
}

::v-deep(ol ol ol > li::before) {
  content: counter(list-counter) '.' counter(sub-list-counter) '.'
    counter(sub-sub-list-counter) '. '; /* Display hierarchical numbering */
  font-weight: bold;
}

::v-deep(ol ol ol ol) {
  counter-reset: sub-sub-sub-list-counter; /* Reset the fourth-level counter */
  list-style: none; /* Remove the default numbering */
  margin-left: 20px; /* Indent for sub-sub-sub-lists */
}

::v-deep(ol ol ol ol > li) {
  counter-increment: sub-sub-sub-list-counter; /* Increment the fourth-level counter */
}

::v-deep(ol ol ol ol > li::before) {
  content: counter(list-counter) '.' counter(sub-list-counter) '.'
    counter(sub-sub-list-counter) '.' counter(sub-sub-sub-list-counter) '. '; /* Display hierarchical numbering */
  font-weight: bold;
}

/* -------------------------------------------------- */
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
