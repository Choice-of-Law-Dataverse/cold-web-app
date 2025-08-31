<template>
  <nav
    class="bg-white border-b border-cold-gray w-full px-6"
    :class="{ 'bg-purple-active': isExpanded }"
  >
    <div
      class="mx-auto py-6 pt-8"
      style="max-width: var(--container-width); width: 100%"
    >
      <div
        class="flex justify-between items-center space-x-4 sm:space-x-8 relative"
      >
        <!-- Search Input -->
        <div class="search-container" :class="{ expanded: isExpanded }">
          <div class="search-input-row">
            <UInput
              size="xl"
              ref="searchInput"
              v-model="searchText"
              @keyup.enter="emitSearch"
              @keydown.esc="clearSearch"
              @focus="expandSearch"
              @blur="collapseSearch"
              class="input-custom-purple placeholder-purple font-semibold"
              :placeholder="searchPlaceholder"
              icon="i-material-symbols:search"
              autocomplete="off"
              :ui="{
                icon: { trailing: { pointer: '' } },
                wrapper: { base: 'h-12' },
                input: { base: 'h-12' },
              }"
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
                  v-show="isExpanded"
                  style="opacity: 1; color: var(--color-cold-night) !important"
                  variant="link"
                  icon="i-material-symbols:close"
                  :padded="false"
                  @mousedown.prevent
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

          <!-- Suggestions -->
          <div
            v-if="isSearchFocused && showSuggestions"
            class="suggestions w-full border-b border-cold-gray"
          >
            <div class="suggestions-inner">
              <div
                v-for="suggestion in suggestions"
                :key="suggestion"
                class="suggestion-item"
                @click="handleSuggestionClick(suggestion)"
              >
                <span class="suggestion-text"
                  >Only show results from {{ suggestion }}</span
                >
              </div>
            </div>
          </div>
        </div>

        <!-- Logo (Hidden when search is expanded) -->
        <NuxtLink
          v-if="!isExpanded"
          to="/"
          class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10 flex items-center justify-center"
        >
          <img
            src="https://choiceoflaw.blob.core.windows.net/assets/cold_beta_logo.svg"
            alt="CoLD Logo"
            class="h-12 w-auto mb-4"
          />
        </NuxtLink>

        <!-- HCCHApproved and Menu/Links Row -->
        <div v-if="!isExpanded" class="flex items-center space-x-4">
          <HCCHApproved v-if="!showMenu" />
          <template v-if="!showMenu">
            <button class="menu-button custom-nav-links" @click="openMenu">
              Menu
            </button>
          </template>
          <template v-else>
            <div class="space-x-3 sm:space-x-6 flex items-center">
              <ULink
                v-for="(link, i) in links"
                :key="i"
                :to="link.to"
                :class="[
                  'custom-nav-links',
                  { active: route.path.startsWith(link.to) },
                ]"
                @click="closeMenu"
              >
                <span>{{ link.label }}</span>
              </ULink>
              <button
                class="close-menu-button ml-2"
                @click="closeMenu"
                aria-label="Close menu"
                style="
                  background: none;
                  border: none;
                  cursor: pointer;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  height: 2.5rem;
                  width: 2.5rem;
                  min-width: 2.5rem;
                  min-height: 2.5rem;
                  z-index: 10;
                "
              >
                <span>
                  <UIcon
                    name="i-material-symbols:close"
                    class="ml-[1em] mt-[0.3em] text-[1.3em]"
                  />
                </span>
              </button>
            </div>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import HCCHApproved from '../ui/HCCHApproved.vue'
import eventBus from '@/eventBus'
import jurisdictionsData from '@/assets/jurisdictions-data.json'
// import your section‐nav configs:
import { aboutNavLinks, learnNavLinks } from '@/config/pageConfigs.js'

const router = useRouter()
const route = useRoute()

// helper to pull off “/about” or “/learn”
// from the first child‐link’s path
const basePath = (arr) => `/${arr[0].path.split('/')[1]}`

const links = [
  { label: 'About', to: basePath(aboutNavLinks) },
  { label: 'Learn', to: basePath(learnNavLinks) },
  { label: 'Contact', to: '/contact' },
]

const showMenu = ref(false)

function openMenu() {
  showMenu.value = true
  // Add click-away listener
  document.addEventListener('mousedown', handleClickAway)
}

function closeMenu() {
  showMenu.value = false
  // Remove click-away listener
  document.removeEventListener('mousedown', handleClickAway)
}

function handleClickAway(e) {
  // Only close if menu is open
  if (!showMenu.value) return
  // Find the nav element
  const nav = document.querySelector('nav')
  if (nav && !nav.contains(e.target)) {
    closeMenu()
  }
}

// Click-away handler for menu
function handleClickOutsideMenu(event) {
  // Only close if menu is open
  if (!showMenu.value) return
  // Find the menu button and menu container
  const nav = document.querySelector('nav')
  // If click is outside nav, close menu
  if (nav && !nav.contains(event.target)) {
    closeMenu()
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutsideMenu)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutsideMenu)
})

// Reactive state
const searchText = ref('')
const isExpanded = ref(false) // Track if the input is expanded
const isSmallScreen = ref(false)
const suggestions = ref([]) // Add suggestions state
const showSuggestions = ref(false) // Add visibility state for suggestions
const isSearchFocused = ref(false)

const searchInput = ref(null)

// Add function to update suggestions
function updateSuggestions() {
  if (!searchText.value || searchText.value.trim().length < 3) {
    suggestions.value = []
    showSuggestions.value = false
    return
  }
  // Only keep words with length >= 3
  const words = searchText.value
    .toLowerCase()
    .split(/\s+/)
    .filter((word) => word.length >= 3)

  let filtered = jurisdictionsData
    .filter((item) =>
      words.some(
        (word) =>
          item.name[0].toLowerCase().includes(word) ||
          item.alternative.some((adj) => adj.toLowerCase().includes(word))
      )
    )
    .map((item) => item.name[0])

  suggestions.value = filtered.slice(0, 5)
  showSuggestions.value = suggestions.value.length > 0
}

// Add function to handle suggestion click
function handleSuggestionClick(selected) {
  const record = jurisdictionsData.find((item) => item.name[0] === selected)
  const keywords = record
    ? [
        record.name[0].toLowerCase().trim(),
        ...record.alternative.map((a) => a.toLowerCase().trim()),
      ]
    : [selected.toLowerCase().trim()]

  const remainingWords = searchText.value
    .split(/\s+/)
    .map((word) => word.trim())
    .filter(
      (word) =>
        !keywords.some((keyword) => keyword.includes(word.toLowerCase()))
    )

  const newSearchText = remainingWords.join(' ')
  searchText.value = newSearchText

  // Explicitly manage search state after suggestion click
  isExpanded.value = false
  isSearchFocused.value = false // Add this to correctly update focus state
  showSuggestions.value = false // This was already here

  const query = { ...route.query }
  if (newSearchText.trim()) {
    query.q = newSearchText.trim()
  } else {
    delete query.q
  }
  query.jurisdiction = selected
  router.push({
    name: 'search',
    query,
  })

  // Blur the input after navigation and state changes
  nextTick().then(() => {
    const inputEl = searchInput.value?.$el.querySelector('input')
    if (inputEl) {
      inputEl.blur() // This blur will call collapseSearch, but relevant states are already set.
    }
  })
}

// Watch search text for suggestions
watch(searchText, () => {
  updateSuggestions()
})

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
  nextTick().then(() => {
    const inputEl = searchInput.value?.$el.querySelector('input')
    if (inputEl) {
      inputEl.blur()
    }
  })
}

function expandSearch() {
  isExpanded.value = true
  isSearchFocused.value = true
  // Suggestions will be updated by the watcher on searchText or if updateSuggestions is called
}

function collapseSearch() {
  isExpanded.value = false // Visual shrink can be immediate

  // Delay setting isSearchFocused to false to allow click event on suggestions
  // to be processed by handleSuggestionClick.
  setTimeout(() => {
    // If isSearchFocused is still true at this point, it means that
    // handleSuggestionClick was not called (or did not set isSearchFocused to false).
    // This implies the blur was to an element outside the suggestions.
    if (isSearchFocused.value) {
      isSearchFocused.value = false
      showSuggestions.value = false // Ensure suggestions are hidden
    }
    // If isSearchFocused was already set to false (e.g., by handleSuggestionClick),
    // this 'if' block is skipped.
    // As a safeguard, ensure showSuggestions is false if isSearchFocused is false.
    else if (!isSearchFocused.value && showSuggestions.value) {
      showSuggestions.value = false
    }
  }, 200) // Original delay
}

const clearSearch = async () => {
  searchText.value = ''
  collapseSearch()
  await nextTick()
  const inputEl = searchInput.value?.$el.querySelector('input')
  if (inputEl) {
    inputEl.blur()
  }
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

function handleGlobalKeydown(e) {
  // Only trigger if not already typing in an input or textarea
  if (
    e.key === 's' &&
    !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)
  ) {
    e.preventDefault() // Prevent default browser actions
    expandSearch()
    nextTick(() => {
      const inputEl = searchInput.value?.$el.querySelector('input')
      if (inputEl) {
        inputEl.focus()
      }
    })
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})

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
  document.removeEventListener('mousedown', handleClickAway)
})
</script>

<style scoped>
.input-custom-purple ::v-deep(.placeholder) {
  color: var(--color-cold-purple) !important;
}

/* Only hide the default left search icon */
.input-custom-purple ::v-deep(.u-input__icon) {
  color: white !important;
  opacity: 0 !important;
}

/* Ensure the clear button icon is visible */
.input-custom-purple ::v-deep(.u-button .iconify) {
  opacity: 1 !important;
  color: var(--color-cold-purple) !important;
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
  position: relative !important; /* New addition */
  width: calc(var(--column-width) * 3 + var(--gutter-width) * 2);
  transition: none !important;
}

/* When expanded, span across available space */
.search-container.expanded {
  width: 100%; /* Expand to full width */
  padding-bottom: 0.625rem;
}

.search-input-row {
  position: relative;
  display: flex;
  align-items: center;
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
  font-weight: 600 !important;
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

/* Outer container now spans the full browser width */
.suggestions {
  position: absolute;
  top: 100%; /* Adjust vertical offset as needed */
  left: 50%;
  transform: translateX(-50%);
  width: 100vw;
  z-index: 1000;
  background-color: var(--color-cold-purple-fake-alpha);
}

/* Inner container now uses full width */
.suggestions-inner {
  width: 100%;
  padding: 0 1.5rem; /* Optional padding */
  box-sizing: border-box;
}

.suggestion-item {
  padding: 12px 16px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.2s;
}

.suggestion-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.suggestion-text {
  font-weight: 500;
  color: var(--color-cold-night);
}

nav {
  min-height: 7rem;
  max-height: 7rem;
}

/* .suggestion-hint {
  font-size: 0.875rem;
  color: var(--color-cold-gray);
  font-style: italic;
} */
</style>
