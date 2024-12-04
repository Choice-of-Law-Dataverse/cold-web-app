<script setup lang="ts">
import { ref } from 'vue'

// Define the tabs with labels and unique keys
const tabs = [
  { label: 'Overview', key: 'overview' },
  { label: 'Team', key: 'team' },
]

// Reactive variable to track the active tab
const activeTab = ref(tabs[0].key)

// Function to set the active tab
const setActiveTab = (key: string) => {
  activeTab.value = key
}
</script>

<template>
  <div class="container">
    <div class="col-span-12">
      <UCard class="cold-ucard">
        <div class="main-content-grid">
          <!-- Tabs Navigation -->
          <div class="grid-item" style="grid-column: 1 / -1">
            <nav
              class="flex space-x-4 border-b border-gray-200 dark:border-gray-800"
            >
              <button
                v-for="tab in tabs"
                :key="tab.key"
                @click="setActiveTab(tab.key)"
                :class="[
                  'px-3 py-2 font-medium text-sm',
                  activeTab === tab.key
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-gray-700',
                ]"
              >
                {{ tab.label }}
              </button>
            </nav>
          </div>

          <!-- Tab Content -->
          <div class="grid-item">
            <div v-if="activeTab === 'overview'">
              <h2>Overview</h2>
              <p>This is the overview section of the About page.</p>
            </div>
            <div v-else-if="activeTab === 'team'">
              <h2>Our Team</h2>
              <p>Meet the amazing team behind this project.</p>
            </div>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<style scoped>
.main-content-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr)); /* 12-column layout */
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
