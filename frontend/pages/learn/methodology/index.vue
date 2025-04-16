<template>
  <main class="px-6">
    <div class="mx-auto w-full" style="max-width: var(--container-width)">
      <UCard class="cold-ucard">
        <!-- Custom Navigation -->
        <nav>
          <div class="nav-wrapper relative">
            <ul
              class="flex items-center space-x-4 border-b border-gray-200 dark:border-gray-800 list-none overflow-x-auto scrollbar-hidden relative z-0"
            >
              <li
                v-for="link in links"
                :key="link.key"
                :class="[
                  'result-value-small cursor-pointer whitespace-nowrap',
                  activeTab === link.key
                    ? 'active font-bold text-cold-purple'
                    : 'text-cold-night',
                ]"
                @click="setActiveTab(link.key)"
              >
                {{ link.label }}
              </li>
            </ul>
            <div class="gray-line"></div>
          </div>
        </nav>

        <!-- Main Content -->
        <div
          class="main-content prose -space-y-10 flex flex-col gap-12 px-6 w-full"
        >
          <ContentDoc path="/methodology_intro" />
          <hr />
          <div id="How-the-Search-Works">
            <ContentDoc path="/methodology_search" />
          </div>
          <hr />
          <!-- Hack -->
          <span id="Questionnaire"></span>
          <div v-html="htmlContent"></div>
        </div>
      </UCard>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { marked } from 'marked' // Import the Markdown parser

// Initialize router and route
const router = useRouter()
const route = useRoute()

// Define the navigation links
const links = [
  { label: 'Open Educational Resources', key: 'open-educational-resources' },
  { label: 'FAQ', key: 'faq' },
  { label: 'Methodology', key: 'methodology' },
  { label: 'Glossary', key: 'glossary' },
  { label: 'Data Sets', key: 'data-sets' },
]

// Reactive variable to track the active tab
const activeTab = ref('methodology')

// Function to set the active tab
const setActiveTab = (key) => {
  router.push(`/learn/${key}`)
}

const content = ref('') // Reactive variable for storing the file content
const htmlContent = ref('') // Store parsed HTML content

onMounted(async () => {
  try {
    const response = await fetch('/methodology_questionnaire.txt') // Fetch the Markdown file
    if (response.ok) {
      content.value = await response.text() // Store raw Markdown
      htmlContent.value = marked(content.value) // Convert Markdown to HTML

      // Check if there's a hash in the URL and scroll to it
      if (window.location.hash) {
        const element = document.getElementById(
          window.location.hash.substring(1)
        )
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' })
        }
      }
    } else {
      console.error('Failed to load text:', response.statusText)
    }
  } catch (error) {
    console.error('Error loading text:', error)
  }
})
</script>

<style scoped>
.nav-wrapper {
  position: relative !important; /* Create a stacking context for children */
  z-index: 0 !important; /* Base stacking layer */
}

.gray-line {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 1px;
  background-color: var(--color-cold-gray);
  z-index: -1;
}

ul {
  overflow-x: auto; /* Ensure scrolling is still functional */
  white-space: nowrap; /* Prevent items from wrapping to the next line */
  position: relative; /* For stacking context */
  border-bottom: 0px solid var(--color-cold-gray); /* Gray line */
  -ms-overflow-style: none; /* Hide scrollbar in IE and Edge */
  scrollbar-width: none; /* Hide scrollbar in Firefox */
}

ul::before {
  content: '';
  position: absolute;
  bottom: 0px;
  left: 0;
  width: 100%;
  height: 1px;
  background-color: var(--color-cold-gray);
  z-index: -1; /* Behind everything */
}

ul::-webkit-scrollbar {
  display: none; /* Hide scrollbar in Chrome, Safari, and Edge */
}

li {
  position: relative !important; /* Enable positioning for the pseudo-element */
  z-index: 1 !important; /* Ensure li is above ul */
}

li.active {
  z-index: 2 !important; /* Bring the active item above the gray line */
}

li.active::after {
  content: ''; /* Creates the underline */
  position: absolute !important;
  left: 0;
  bottom: -9px; /* Moves the underline down by 4px */
  width: 100%;
  height: 2px; /* Thickness of the underline */
  background-color: var(--color-cold-purple); /* Underline color */
  z-index: 3 !important; /* Ensure the underline is above the gray line */
  pointer-events: none; /* Avoid interaction blocking */
}

/* Ensure no default list styles appear */
.list-none {
  list-style: none !important;
}

/* Add some spacing and hover effects to the navigation links */
.flex li {
  padding: 0.5rem 1rem;
}

::v-deep(ul) {
  list-style-type: disc !important;
  padding-left: 12px !important;
}

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
