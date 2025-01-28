<template>
  <nav class="bg-white border-b border-cold-gray w-full px-6 h-[110px]">
    <div
      class="mx-auto h-full"
      style="max-width: var(--container-width); width: 100%"
    >
      <div
        class="flex items-center justify-between h-full space-x-4 sm:space-x-8"
      >
        <!-- Web App Name aligned to the first column -->
        <div>
          <h1>
            <a href="/" class="font-bold text-cold-night">CoLD</a>
          </h1>
        </div>

        <!-- Search Input positioned from the center of column 2 to the end of column 10 -->
        <div class="search-container">
          <UInput
            size="xl"
            v-model="searchText"
            @keyup.enter="emitSearch"
            class="input-custom-purple placeholder-purple"
            :placeholder="searchPlaceholder"
            icon="i-material-symbols:search"
            :trailing="true"
            style="
              width: 100%; /* Full width inside the container */
              border-radius: 0 !important;
              box-shadow: none !important;
              border-width: 1px !important;
              border-color: var(--color-cold-purple) !important;
            "
          />
          <button @click="emitSearch" class="icon-button">
            <span
              class="iconify i-material-symbols:search"
              aria-hidden="true"
            ></span>
          </button>
        </div>

        <!-- Navigation Links, aligned in columns 11 and 12 -->
        <div class="space-x-4 sm:space-x-8">
          <ULink
            v-for="(link, index) in links"
            :key="index"
            :to="link.to"
            :class="['custom-nav-links', { active: route.path === link.to }]"
          >
            <span>{{ link.label }}</span>
          </ULink>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import eventBus from '@/eventBus'

// Reactive state
const searchText = ref('')
const isSmallScreen = ref(false)

const router = useRouter()
const route = useRoute()

const links = [
  { label: 'About', to: '/about' },
  { label: 'Contact', to: '/contact' },
]

function emitSearch() {
  const query = { ...route.query } // Retain existing query parameters (filters)

  if (searchText.value.trim()) {
    // Update the search query if there's input
    query.q = searchText.value.trim()
  } else {
    // Remove the search query (q) if the input is empty
    delete query.q
  }

  // Push the updated query to the router
  router.push({
    name: 'search',
    query,
  })
}

// Dynamically update the placeholder
const searchPlaceholder = computed(() =>
  isSmallScreen.value ? 'Search' : 'Search the entire Dataverse'
)

// Check screen size
function checkScreenSize() {
  isSmallScreen.value = window.innerWidth < 640 // Tailwind's `sm` breakpoint
}

// Listen for events from PopularSearches.vue
const updateSearchFromEvent = (query) => {
  searchText.value = query // Update the search input field
}

// Lifecycle hooks
onMounted(() => {
  // Initialize screen size
  checkScreenSize()

  // Add resize event listener
  window.addEventListener('resize', checkScreenSize)

  // Initialize search text from query
  if (route.query.q) {
    searchText.value = route.query.q
  }

  // Listen for events from PopularSearches.vue
  eventBus.on('update-search', updateSearchFromEvent)
})

onUnmounted(() => {
  // Clean up event listeners
  window.removeEventListener('resize', checkScreenSize)
  eventBus.off('update-search', updateSearchFromEvent)
})
</script>

<style scoped>
.input-custom-purple ::v-deep(.placeholder) {
  color: var(--color-cold-purple) !important;
}

/* Make the original input's icon white and thus invisible */
/* I.e., the icon that's not clickable */
.input-custom-purple ::v-deep(.iconify) {
  color: white !important;
  opacity: 0 !important;
}

.input-custom-purple ::placeholder {
  color: var(--color-cold-purple) !important;
  opacity: 1;
}

.inner-content {
  max-width: var(--container-width);
  margin: 0 auto;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.search-container {
  position: relative; /* Allow absolute positioning for icon */
  width: calc(
    var(--column-width) * 9 + var(--gutter-width) * 8
  ); /* 9-column width */
  margin-left: calc(var(--column-width) / 2);
}

.input-custom-purple {
  width: 100%; /* Ensures the input spans the container width */
}

.icon-button {
  position: absolute;
  right: 10px; /* Adjust based on the right padding of input */
  top: 50%;
  transform: translateY(-39%); /* Center vertically */
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-cold-purple); /* Match icon color */
  padding: 0;
}

.icon-button .iconify {
  font-size: 1.5rem; /* Adjust icon size */
}

a {
  color: var(--color-cold-night) !important;
  text-decoration: none !important;
}

:deep(.custom-nav-links) {
  color: var(--color-cold-night) !important; /* Apply custom color */
  text-decoration: none !important; /* Remove underline */
  /*margin-left: 48px;*/
  font-weight: 600;
}

:deep(.custom-nav-links.active) {
  text-decoration: underline !important;
  text-underline-offset: 6px !important;
  text-decoration-thickness: 2px !important;
  text-decoration-color: var(--color-cold-purple) !important;
}
</style>
