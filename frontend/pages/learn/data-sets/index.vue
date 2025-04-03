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
        <div class="main-conten prose -space-y-10 flex flex-col gap-12 px-6 w-full">
          <ContentDoc path="/data_sets" />
        </div>
      </UCard>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

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
const activeTab = ref('data-sets')

// Function to set the active tab
const setActiveTab = (key) => {
  router.push(`/learn/${key}`)
}
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

.main-conten {
  max-width: var(--container-width);
  margin: 0 auto;
  width: 100%;
}
</style> 