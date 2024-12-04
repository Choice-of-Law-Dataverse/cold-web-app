<script setup lang="ts">
import { ref } from 'vue'
import Overview from './Overview.vue'
import Team from './Team.vue'

// Define the navigation links
const links = [
  { label: 'Overview', key: 'overview' },
  { label: 'Team', key: 'team' },
]

// Reactive variable to track the active tab
const activeTab = ref('overview')

// Function to set the active tab
const setActiveTab = (key) => {
  activeTab.value = key
}
</script>

<template>
  <div class="container">
    <div class="col-span-12">
      <UCard class="cold-ucard">
        <div class="main-content-grid">
          <!-- Horizontal Navigation -->
          <div class="grid-item" style="grid-column: 1 / -1">
            <UHorizontalNavigation
              :links="
                links.map((link) => ({
                  ...link,
                  click: () => setActiveTab(link.key),
                }))
              "
              class="border-b border-gray-200 dark:border-gray-800"
            />
          </div>

          <!-- Tab Content -->
          <div v-if="activeTab === 'overview'">
            <Overview />
          </div>
          <div v-else-if="activeTab === 'team'">
            <Team />
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<style scoped>
.main-content-grid {
  display: grid;
  /*grid-template-columns: repeat(12, minmax(0, 1fr)); /* 12-column layout */
  column-gap: var(--gutter-width); /* Gutter space between columns */
  padding: 32px; /* Optional padding to match the card's interior padding */
}

.grid-item {
  margin-bottom: 48px; /* Space between items */
}

p {
  margin-bottom: 36px;
}

h2 {
  margin-bottom: 8px;
}
</style>
