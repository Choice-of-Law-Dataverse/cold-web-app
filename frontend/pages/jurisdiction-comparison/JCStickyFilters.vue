<template>
  <div>
    <!-- Desktop/Tablet Sticky Filters -->
    <div
      class="jc-fixed-filters -mb-16 hidden md:block"
      :class="{ 'jc-fixed-filters-bg': isSticky }"
    >
      <div class="jc-sticky-grid jc-overview-row">
        <div></div>
        <div
          v-for="(filter, index) in jurisdictionFilters"
          :key="`desktop-filter-${index}`"
        >
          <SearchFilters
            :options="jurisdictionOptions"
            v-model="filter.value.value"
            class="jc-search-filter"
            showAvatars="true"
            :multiple="false"
          />
        </div>
      </div>
    </div>

    <!-- Mobile/Tablet Filters Grid -->
    <div class="md:hidden">
      <div class="filters-grid mb-6">
        <div
          v-for="(filter, index) in jurisdictionFilters"
          :key="`mobile-filter-${index}`"
          class="filter-item"
        >
          <SearchFilters
            :options="jurisdictionOptions"
            v-model="filter.value.value"
            class="w-full"
            showAvatars="true"
            :multiple="false"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import SearchFilters from '@/components/search-results/SearchFilters.vue'

// Initialize jurisdiction options with default value
const jurisdictionOptions = ref([{ label: 'All Jurisdictions' }])

// Create reactive filter references
const currentJurisdictionFilter1 = ref([])
const currentJurisdictionFilter2 = ref([])
const currentJurisdictionFilter3 = ref([])

// Create computed array for easier iteration
const jurisdictionFilters = computed(() => [
  { value: currentJurisdictionFilter1 },
  { value: currentJurisdictionFilter2 },
  { value: currentJurisdictionFilter3 },
])

// Sticky state for background
const isSticky = ref(false)

// Data fetching
const loadJurisdictions = async () => {
  try {
    const config = useRuntimeConfig()
    const response = await fetch(
      `${config.public.apiBaseUrl}/search/full_table`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ table: 'Jurisdictions', filters: [] }),
      }
    )

    if (!response.ok) throw new Error('Failed to load jurisdictions')

    const jurisdictionsData = await response.json()
    jurisdictionOptions.value = [
      { label: 'All Jurisdictions' },
      ...jurisdictionsData
        .filter((entry) => entry['Irrelevant?'] === null)
        .map((entry) => ({
          label: entry.Name,
          avatar: entry['Alpha-3 Code']
            ? `https://choiceoflawdataverse.blob.core.windows.net/assets/flags/${entry['Alpha-3 Code'].toLowerCase()}.svg`
            : undefined,
        }))
        .sort((a, b) => (a.label || '').localeCompare(b.label || '')),
    ]
  } catch (error) {
    console.error('Error loading jurisdictions:', error)
  }
}

// Initialization
onMounted(async () => {
  await loadJurisdictions()

  // JavaScript-based sticky implementation
  const filtersElement = document.querySelector('.jc-fixed-filters')
  const overviewElement = document.querySelector('.jc-z-top')

  if (!filtersElement || !overviewElement) return

  // Get the initial position of the filters relative to the Overview title
  const getOverviewTop = () => {
    const overviewRect = overviewElement.getBoundingClientRect()
    return overviewRect.top + window.scrollY
  }

  let overviewTop = getOverviewTop()

  const onScroll = () => {
    const scrollTop = window.scrollY

    // Recalculate overview position (in case layout changes)
    overviewTop = getOverviewTop()

    // Check if we've scrolled past the Overview title
    if (scrollTop > overviewTop - 80) {
      // 80px offset for better UX
      // Make filters sticky at top of viewport
      filtersElement.style.position = 'fixed'
      filtersElement.style.top = '0'
      filtersElement.style.left = '0'
      filtersElement.style.right = '0'
      filtersElement.style.width = '100%'
      filtersElement.style.zIndex = '1000'
      isSticky.value = true
    } else {
      // Reset to normal flow
      filtersElement.style.position = 'static'
      filtersElement.style.top = 'auto'
      filtersElement.style.left = 'auto'
      filtersElement.style.right = 'auto'
      filtersElement.style.width = 'auto'
      filtersElement.style.zIndex = 'auto'
      isSticky.value = false
    }
  }

  window.addEventListener('scroll', onScroll)
  window.addEventListener('resize', () => {
    overviewTop = getOverviewTop()
    onScroll()
  })
  onScroll() // Call once to set initial state
})
</script>

<style scoped>
.jc-fixed-filters {
  position: static; /* Will be controlled by JavaScript */
  top: 0;
  z-index: 1000;
  background: transparent;
  /* padding: 1em 0; */
  width: 100%;
  /* transition: background-color 0.2s ease; */
}

.jc-fixed-filters > * {
  max-width: var(--container-width, 1200px);
  margin: 0 auto;
  /* padding: 0 1.5rem; */
}

.jc-fixed-filters-bg {
  background: #fff;
  border-bottom: 1px solid var(--color-cold-gray);
  /* box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); */
  padding-top: 1rem;
  padding-bottom: 1rem;
}

.jc-sticky-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 0 1.5rem;
  align-items: end;
  width: 100%;
}

.jc-sticky-grid > div {
  /* Ensures SearchFilters fill their columns */
  min-width: 0;
}

/* Filters grid for mobile */
.filters-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 640px) {
  .filters-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 768px) {
  .filters-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.filter-item {
  display: flex;
  flex-direction: column;
}
</style>
