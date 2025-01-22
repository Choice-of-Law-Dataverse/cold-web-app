<template>
  <main class="px-6">
    <div class="mx-auto w-full" style="max-width: var(--container-width)">
      <UCard class="cold-ucard">
        <!-- Custom Navigation -->
        <nav class="custom-nav">
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
              @click="setActiveTab(link.key)"
            >
              {{ link.label }}
            </li>
          </ul>
        </nav>

        <!-- Main Content -->
        <div
          class="main-conten prose -space-y-10 flex flex-col gap-12 px-6 w-full"
        >
          <!-- Tab Content -->
          <div v-if="activeTab === 'overview'">
            <Overview />
          </div>
          <div v-else-if="activeTab === 'open-educational-resources'">
            <OpenEducationalResources />
          </div>
          <div v-else-if="activeTab === 'faq'">
            <FAQ />
          </div>
          <div v-else-if="activeTab === 'team'">
            <Team />
          </div>
          <div v-else-if="activeTab === 'press'">
            <Press />
          </div>
        </div>
      </UCard>
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

::v-deep(ul) {
  list-style-type: disc !important;
  padding-left: 12px !important;
}
</style>
