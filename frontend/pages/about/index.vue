<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <UCard class="cold-ucard">
          <!-- Custom Navigation -->
          <div class="custom-nav">
            <nav>
              <ul
                class="flex space-x-4 border-b border-gray-200 dark:border-gray-800 list-none"
              >
                <li
                  v-for="link in links"
                  :key="link.key"
                  :class="[
                    'result-value-small cursor-pointer',
                    activeTab === link.key
                      ? 'active font-bold text-cold-purple'
                      : 'text-cold-night',
                  ]"
                  :style="
                    activeTab === link.key
                      ? {
                          color: 'var(--color-cold-purple)',
                          borderColor: 'var(--color-cold-purple)',
                        }
                      : {}
                  "
                  @click="setActiveTab(link.key)"
                >
                  {{ link.label }}
                </li>
              </ul>
            </nav>
          </div>
          <div class="main-content-grid">
            <div class="grid-item">
              <!-- Tab Content -->

              <div v-if="activeTab === 'overview'">
                <Overview />
              </div>
              <div v-if="activeTab === 'open-educational-resources'">
                <OpenEducationalResources />
              </div>
              <div v-if="activeTab === 'faq'">
                <FAQ />
              </div>
              <div v-else-if="activeTab === 'team'">
                <Team />
              </div>
              <div v-else-if="activeTab === 'press'">
                <Press />
              </div>
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Overview from './Overview.vue'
import OpenEducationalResources from './OpenEducationalResources.vue'
import FAQ from './FAQ.vue'
import Team from './Team.vue'
import Press from './Press.vue'

// Define the navigation links
const links = [
  { label: 'Overview', key: 'overview' },
  { label: 'Open Educational Resources', key: 'open-educational-resources' },
  { label: 'FAQ', key: 'faq' },
  { label: 'Team', key: 'team' },
  { label: 'Press', key: 'press' },
]

// Initialize router and route
const router = useRouter()
const route = useRoute()

// Reactive variable to track the active tab, default to 'overview'
const activeTab = ref(route.query.tab || 'overview')

// Watch for changes in activeTab and update the URL query
watch(activeTab, (newTab) => {
  router.replace({ query: { ...route.query, tab: newTab } })
})

// Function to set the active tab
const setActiveTab = (key) => {
  activeTab.value = key
}
</script>

<style scoped>
ul {
  border-bottom: 1px solid var(--color-cold-gray); /* Gray line */
  position: relative;
}

li {
  padding-bottom: 0px !important; /* Adjust spacing between text and gray line */
}

li.active {
  border-bottom: 1px solid var(--color-cold-purple) !important; /* Active item underline */
  margin-bottom: -1px !important; /* Offset to align with the gray line */
}

.custom-nav {
  margin-top: 32px;
  margin-left: 12px;
}

/* Ensure no default list styles appear */
.list-none {
  list-style: none !important;
}

/* Add some spacing and hover effects to the navigation links */
.flex li {
  padding: 0.5rem 1rem;
  transition: color 0.3s ease;
}

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

p {
  margin-bottom: 36px;
}

::v-deep(h2) {
  margin-top: 20px;
}

::v-deep(ul) {
  list-style-type: disc !important;
  padding-left: 12px !important;
  margin: -32px 0 0 0 !important;
}

::v-deep(li) {
  margin-bottom: -18px; /* Optional spacing between list items */
}
</style>
