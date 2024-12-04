<template>
  <div class="container">
    <div class="col-span-12">
      <UCard class="cold-ucard">
        <div class="main-content-grid">
          <!-- Horizontal Navigation -->
          <div class="grid-item">
            <UHorizontalNavigation
              :links="
                links.map((link) => ({
                  ...link,
                  click: () => setActiveTab(link.key),
                }))
              "
              class="border-b border-gray-200 dark:border-gray-800"
            />

            <!-- Tab Content -->

            <div v-if="activeTab === 'overview'">
              <Overview />
            </div>

            <div v-else-if="activeTab === 'team'">
              <Team />
            </div>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Overview from './Overview.vue'
import Team from './Team.vue'

// Define the navigation links
const links = [
  { label: 'Overview', key: 'overview' },
  { label: 'Team', key: 'team' },
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

h2 {
  margin-bottom: 8px;
}
</style>
