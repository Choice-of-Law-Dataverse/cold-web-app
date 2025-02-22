<template>
  <nav
    class="bg-white border-b border-cold-gray w-full px-6 h-[110px]"
    :class="{ 'bg-purple-active': isExpanded }"
  >
    <div
      class="mx-auto h-full"
      style="max-width: var(--container-width); width: 100%"
    >
      <div
        class="flex items-center justify-between h-full space-x-4 sm:space-x-8"
      >
        <!-- Search Input -->
        <div class="search-container" :class="{ expanded: isExpanded }">
          <UInput
            size="xl"
            v-model="searchText"
            @keyup.enter="emitSearch"
            @focus="expandSearch"
            @blur="collapseSearch"
            class="input-custom-purple placeholder-purple font-semibold"
            :placeholder="searchPlaceholder"
            icon="i-material-symbols:search"
            autocomplete="off"
            :ui="{ icon: { trailing: { pointer: '' } } }"
            :style="{
              width: '100%',
              borderRadius: '0',
              boxShadow: 'none',
              border: 'none',
              backgroundColor: isExpanded
                ? 'transparent'
                : 'var(--color-cold-purple-alpha)',
            }"
          >
            <template #trailing>
              <UButton
                v-show="searchText !== ''"
                color="gray"
                variant="link"
                icon="i-heroicons-x-mark-20-solid"
                :padded="false"
                @click="clearSearch"
              />
            </template>
          </UInput>
          <button @click="emitSearch" class="icon-button">
            <span
              class="iconify i-material-symbols:search"
              aria-hidden="true"
            ></span>
          </button>
        </div>
        <!-- Logo (Hidden when search is expanded) -->
        <div v-if="!isExpanded" class="flex-1 flex justify-center items-center">
          <a href="/">
            <img
              src="https://choiceoflawdataverse.blob.core.windows.net/assets/cold_logo.svg"
              alt="CoLD Logo"
              class="h-6 w-auto"
            />
          </a>
        </div>

        <!-- Navigation Links (Always visible) -->
        <div v-if="!isExpanded" class="space-x-3 sm:space-x-6">
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
const isExpanded = ref(false) // Track if the input is expanded
const isSmallScreen = ref(false)

const router = useRouter()
const route = useRoute()

const links = [
  { label: 'About', to: '/about' },
  { label: 'Learn', to: '/learn' },
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
  collapseSearch() // Shrink search field after search
}

function expandSearch() {
  isExpanded.value = true
}

function collapseSearch() {
  isExpanded.value = false
}

const clearSearch = () => {
  searchText.value = ''
}

// Dynamically update the placeholder
const searchPlaceholder = computed(() =>
  isSmallScreen.value ? 'Search' : 'Search'
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
/* .input-custom-purple ::v-deep(.iconify) {
  color: white !important;
  opacity: 0 !important;
} */

/* Only hide the default left search icon */
.input-custom-purple ::v-deep(.u-input__icon) {
  color: white !important;
  opacity: 0 !important;
}

/* Ensure the clear button icon is visible */
.input-custom-purple ::v-deep(.u-button .iconify) {
  opacity: 1 !important;
  color: var(--color-cold-purple) !important;
  /* z-index: 999 !important; */
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
  width: calc(var(--column-width) * 3 + var(--gutter-width) * 2);
  /* transition: width 0.8s ease-in-out; */
  transition: none !important;
}

/* When expanded, span across available space */
.search-container.expanded {
  width: 100%; /* Expand to full width */
}

.input-custom-purple {
  width: 100%; /* Ensures the input spans the container width */
}

.icon-button {
  position: absolute;
  left: 10px; /* Adjust based on the right padding of input */
  top: 50%;
  transform: translateY(-39%); /* Center vertically */
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-cold-purple); /* Match icon color */
  padding: 0;
  padding-left: 4px;
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

.bg-purple-active {
  background-color: var(--color-cold-purple-alpha) !important;
}
</style>
