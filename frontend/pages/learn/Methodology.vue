<template>
  <div class="main-content prose -space-y-10 flex flex-col gap-12 w-full">
    <ContentDoc path="/methodology_intro" />
    <hr />
    <ContentDoc path="/methodology_search" />
    <hr />
    <!-- Hack -->
    <span id="questionnaire"></span>
    <div v-html="htmlContent"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { marked } from 'marked' // Import the Markdown parser

const content = ref('') // Reactive variable for storing the file content
const htmlContent = ref('') // Store parsed HTML content

onMounted(async () => {
  try {
    const response = await fetch('/methodology_questionnaire.txt') // Fetch the Markdown file
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
/* Add consistent spacing between list items */
::v-deep(ol > li),
::v-deep(ol ol > li),
::v-deep(ol ol ol > li),
::v-deep(ol ol ol ol > li) {
  margin-bottom: 24px !important; /* Adjust as needed for consistent spacing*/
}

/* Ensure sub-lists are indented without extra spacing */
::v-deep(ol ol),
::v-deep(ol ol ol),
::v-deep(ol ol ol ol) {
  /* margin-top: 24px !important; */
  /* margin-bottom: 24px !important; */
}

/* Reset the counter for the top-level list */
::v-deep(ol) {
  counter-reset: list-counter; /* Initialize the counter */
  list-style: none !important; /* Remove the default numbering */
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
  list-style: none !important; /* Remove the default numbering */
  margin-left: 24px; /* Indent for sub-lists */
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
  list-style: none !important; /* Remove the default numbering */
  margin-left: 24px; /* Indent for sub-sub-lists */
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
  list-style: none !important; /* Remove the default numbering */
  margin-left: 24px; /* Indent for sub-sub-sub-lists */
}

::v-deep(ol ol ol ol > li) {
  counter-increment: sub-sub-sub-list-counter; /* Increment the fourth-level counter */
}

::v-deep(ol ol ol ol > li::before) {
  content: counter(list-counter) '.' counter(sub-list-counter) '.'
    counter(sub-sub-list-counter) '.' counter(sub-sub-sub-list-counter) '. '; /* Display hierarchical numbering */
  font-weight: bold;
}
</style>
