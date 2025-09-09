<template>
  <div>
    <!-- Desktop/Tablet Sticky Filters -->
    <div
      class="jc-fixed-filters -mb-[72px] hidden md:block"
      :class="{ 'jc-fixed-filters-bg': isSticky }"
    >
      <div class="jc-sticky-grid jc-overview-row">
        <div style="grid-column: 1">
          <h2 v-show="!isSticky" class="mb-1">Overview</h2>
          <div
            v-show="isSticky"
            style="visibility: hidden; height: 1.5em"
          ></div>
        </div>
        <div
          v-for="(filter, index) in jurisdictionFilters"
          :key="`desktop-filter-${index}`"
          :style="`grid-column: ${index + 2}`"
        >
          <SearchFilters
            :options="jurisdictionOptions"
            v-model="filter.value.value"
            class="jc-search-filter"
            :showAvatars="true"
            :multiple="false"
            :loading="loadingJurisdictions"
          />
        </div>
        <div
          v-if="!showThirdColumn"
          class="jc-add-col"
          style="grid-column: 4; align-self: end"
        >
          <button class="btn-add" @click="showThirdColumn = true">
            + Add third jurisdiction
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile/Tablet Filters Grid -->
    <div class="md:hidden">
      <h2 class="text-xl font-semibold mb-8">Compare Jurisdictions</h2>
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
            :showAvatars="true"
            :multiple="false"
            :loading="loadingJurisdictions"
          />
        </div>
        <div v-if="!showThirdColumn" class="mt-2">
          <button class="btn-add w-full" @click="showThirdColumn = true">
            + Add third jurisdiction
          </button>
        </div>
        <hr class="jc-hr mt-4" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import SearchFilters from '@/components/search-results/SearchFilters.vue'
import { useJurisdictionComparison } from '@/composables/useJurisdictionComparison'

// Props for initial countries from URL
const props = defineProps({
  initialCountries: {
    type: Array,
    default: () => [],
  },
})

// Router for URL updates
const router = useRouter()
const route = useRoute()

// Use shared jurisdiction comparison state
const {
  currentJurisdictionFilter1,
  currentJurisdictionFilter2,
  currentJurisdictionFilter3,
  jurisdictionOptions,
  loadingJurisdictions,
  jurisdictionFilters,
  loadJurisdictions,
  setInitialFilters,
  showThirdColumn,
} = useJurisdictionComparison()

// Sticky state for background
const isSticky = ref(false)

// Watch for changes in initialCountries prop
watch(
  () => props.initialCountries,
  () => {
    if (jurisdictionOptions.value.length > 1) {
      // Ensure jurisdictions are loaded
      setInitialFilters(jurisdictionOptions.value, props.initialCountries)
    }
  },
  { immediate: true }
)

// Watch for changes in filter selections and update URL
watch(
  [
    currentJurisdictionFilter1,
    currentJurisdictionFilter2,
    currentJurisdictionFilter3,
    showThirdColumn,
  ],
  () => {
    const f1 = currentJurisdictionFilter1.value[0]?.alpha3Code?.toLowerCase()
    const f2 = currentJurisdictionFilter2.value[0]?.alpha3Code?.toLowerCase()
    const f3 = currentJurisdictionFilter3.value[0]?.alpha3Code?.toLowerCase()

    // Require at least two to build URL
    if (f1 && f2) {
      const parts = [f1, f2]
      if (showThirdColumn.value && f3) parts.push(f3)
      const countryCodes = parts.join('+')
      const currentCountries = route.params.countries
      if (currentCountries !== countryCodes) {
        router.push(`/jurisdiction-comparison/${countryCodes}`)
      }
    }
  },
  { deep: true }
)

// Initialization
onMounted(async () => {
  await loadJurisdictions()

  // Set initial filters after loading
  if (jurisdictionOptions.value.length > 1) {
    setInitialFilters(jurisdictionOptions.value, props.initialCountries)
  }

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
      // Make filters sticky at top of viewport but constrained to container width
      filtersElement.style.position = 'fixed'
      filtersElement.style.top = '0'
      filtersElement.style.left = '0'
      filtersElement.style.right = '0'
      filtersElement.style.transform = 'none'
      filtersElement.style.width = '100%'
      filtersElement.style.maxWidth = 'var(--container-width, 1200px)'
      filtersElement.style.margin = '0 auto'
      filtersElement.style.zIndex = '1000'
      isSticky.value = true
    } else {
      // Reset to normal flow
      filtersElement.style.position = 'static'
      filtersElement.style.top = 'auto'
      filtersElement.style.left = 'auto'
      filtersElement.style.right = 'auto'
      filtersElement.style.transform = 'none'
      filtersElement.style.width = 'auto'
      filtersElement.style.maxWidth = 'none'
      filtersElement.style.margin = ''
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
  z-index: 10001 !important;
  background: transparent;
  width: 100%;
}

/* Removed 2-column grid media query */
.jc-fixed-filters-bg {
  background: #fff;
  border-bottom: 1px solid var(--color-cold-gray);
  padding-top: 1rem;
  padding-bottom: 1rem;
  z-index: 10001 !important;
}

.jc-sticky-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr; /* label + up to 3 filters */
  align-items: end;
  width: 100%;
  min-width: 600px; /* Ensures enough space for columns + gaps */
  column-gap: 24px !important;
}

/* Filters grid for mobile */
.filters-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .filters-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.filter-item {
  display: flex;
  flex-direction: column;
}

.btn-add {
  background: var(--color-cold-purple);
  color: #fff;
  border-radius: 6px;
  padding: 8px 12px;
  font-weight: 600;
}
</style>
