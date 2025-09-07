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
            :options="jurisdictions"
            v-model="filter.value.value"
            class="jc-search-filter"
            :showAvatars="true"
            :multiple="false"
            :loading="loadingJurisdictions"
          />
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
            :options="jurisdictions"
            v-model="filter.value.value"
            class="w-full"
            :showAvatars="true"
            :multiple="false"
            :loading="loadingJurisdictions"
          />
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

const { data: jurisdictions, isLoading: loadingJurisdictions } =
  useJurisdictions()

// Use shared jurisdiction comparison state
const {
  currentJurisdictionFilter1,
  currentJurisdictionFilter2,
  currentJurisdictionFilter3,
  jurisdictionFilters,
  setInitialFilters,
} = useJurisdictionComparison()

// Sticky state for background
const isSticky = ref(false)

// Watch for changes in initialCountries prop
watch(
  () => props.initialCountries,
  () => {
    if (jurisdictions.value.length > 1) {
      // Ensure jurisdictions are loaded
      setInitialFilters(jurisdictions.value, props.initialCountries)
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
  ],
  () => {
    // Only update URL if all three filters have selections and we have alpha3 codes
    const filter1 = currentJurisdictionFilter1.value[0]
    const filter2 = currentJurisdictionFilter2.value[0]
    const filter3 = currentJurisdictionFilter3.value[0]

    if (filter1?.alpha3Code && filter2?.alpha3Code && filter3?.alpha3Code) {
      const countryCodes = [
        filter1.alpha3Code.toLowerCase(),
        filter2.alpha3Code.toLowerCase(),
        filter3.alpha3Code.toLowerCase(),
      ].join('+')

      // Only update if the URL would actually change
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
  // Set initial filters after loading
  if (jurisdictions.value.length > 1) {
    setInitialFilters(jurisdictions.value, props.initialCountries)
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
  grid-template-columns: 1fr 1fr 1fr 1fr;
  align-items: end;
  width: 100%;
  min-width: 600px; /* Ensures enough space for 4 columns + gaps */
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
    grid-template-columns: repeat(3, 1fr);
  }
}

.filter-item {
  display: flex;
  flex-direction: column;
}
</style>
