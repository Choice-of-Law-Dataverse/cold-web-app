<template>
  <div>
    <!-- Desktop/Tablet Sticky Filters -->
    <div
      class="jc-fixed-filters -mb-[72px] hidden md:block"
      :class="{ 'jc-fixed-filters-bg': isSticky }"
    >
      <div class="jc-sticky-wrap">
        <div
          class="jc-sticky-grid jc-overview-row"
          :class="showThirdColumn ? 'cols-3' : 'cols-2'"
        >
          <div style="grid-column: 1">
            <h2 v-show="!isSticky" class="mb-1">Overview</h2>
            <div v-show="isSticky" class="invisible h-6" />
          </div>

          <!-- Two jurisdictions: align with columns 2 and 3 -->
          <template v-if="!showThirdColumn">
            <div style="grid-column: 2">
              <SearchFilters
                :options="jurisdictions"
                v-model="jurisdictionFilters[0].value.value"
                class="jc-search-filter"
                :showAvatars="true"
                :multiple="false"
                :loading="loadingJurisdictions"
              />
            </div>
            <div style="grid-column: 3">
              <div class="jc-right-cell">
                <SearchFilters
                  :options="jurisdictions"
                  v-model="jurisdictionFilters[1].value.value"
                  class="jc-search-filter"
                  :showAvatars="true"
                  :multiple="false"
                  :loading="loadingJurisdictions"
                />
                <button
                  type="button"
                  class="jc-add-link mb-2"
                  @click="showThirdColumn = true"
                  aria-label="Add third jurisdiction"
                  title="Add third jurisdiction"
                >
                  <Icon
                    name="i-material-symbols:add-circle-outline"
                    class="ml-8 mr-2 text-[20px]"
                  />
                  Add
                </button>
              </div>
            </div>
          </template>

          <!-- Three jurisdictions: columns 2, 3, 4 -->
          <template v-else>
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
          </template>
        </div>
      </div>
    </div>

    <!-- Mobile/Tablet Filters Grid -->
    <div class="md:hidden">
      <h2 class="mb-8 text-xl font-semibold">Compare Jurisdictions</h2>
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
          <!-- Mobile: Add third jurisdiction below second dropdown -->
          <button
            v-if="!showThirdColumn && index === 1"
            type="button"
            class="jc-add-link mt-4"
            @click="showThirdColumn = true"
            aria-label="Add third jurisdiction"
            title="Add third jurisdiction"
          >
            <Icon
              name="i-material-symbols:add-circle-outline"
              class="mr-2 text-[20px]"
            />
            Add Jurisdiction
          </button>
        </div>

        <hr class="jc-hr mt-4" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import SearchFilters from "@/components/search-results/SearchFilters.vue";
import { useJurisdictionComparison } from "@/composables/useJurisdictionComparison";
import { useJurisdictions } from "@/composables/useJurisdictions";

// Props for initial countries from URL
const props = defineProps({
  initialCountries: {
    type: Array,
    default: () => [],
  },
});

// Router for URL updates
const router = useRouter();
const route = useRoute();

const { data: jurisdictions, isLoading: loadingJurisdictions } =
  useJurisdictions();

// Use shared jurisdiction comparison state
const {
  currentJurisdictionFilter1,
  currentJurisdictionFilter2,
  currentJurisdictionFilter3,
  jurisdictionFilters,
  setInitialFilters,
  showThirdColumn,
} = useJurisdictionComparison();

// Sticky state for background
const isSticky = ref(false);

// Watch for changes in jurisdictions data and initialCountries prop
watch(
  [() => jurisdictions?.value, () => props.initialCountries],
  ([jurisdictionsData, initialCountries]) => {
    if (jurisdictionsData?.length > 1 && initialCountries?.length > 0) {
      setInitialFilters(jurisdictionsData, initialCountries);
    }
  },
  { immediate: true },
);

// Watch for changes in filter selections and update URL
watch(
  [
    currentJurisdictionFilter1,
    currentJurisdictionFilter2,
    currentJurisdictionFilter3,
    showThirdColumn,
  ],
  () => {
    const f1 = currentJurisdictionFilter1.value[0]?.alpha3Code?.toLowerCase();
    const f2 = currentJurisdictionFilter2.value[0]?.alpha3Code?.toLowerCase();
    const f3 = currentJurisdictionFilter3.value[0]?.alpha3Code?.toLowerCase();

    // Require at least two to build URL
    if (f1 && f2) {
      const parts = [f1, f2];
      if (showThirdColumn.value && f3) parts.push(f3);
      const countryCodes = parts.join("+");
      const currentCountries = route.params.countries;
      if (currentCountries !== countryCodes) {
        router.push(`/jurisdiction-comparison/${countryCodes}`);
      }
    }
  },
  { deep: true },
);

// Initialization
onMounted(async () => {
  // JavaScript-based sticky implementation
  const filtersElement = document.querySelector(".jc-fixed-filters");
  const overviewElement = document.querySelector(".jc-z-top");

  if (!filtersElement || !overviewElement) return;

  // Get the initial position of the filters relative to the Overview title
  const getOverviewTop = () => {
    const overviewRect = overviewElement.getBoundingClientRect();
    return overviewRect.top + window.scrollY;
  };

  let overviewTop = getOverviewTop();

  const onScroll = () => {
    const scrollTop = window.scrollY;

    // Recalculate overview position (in case layout changes)
    overviewTop = getOverviewTop();

    // Check if we've scrolled past the Overview title
    if (scrollTop > overviewTop - 80) {
      // 80px offset for better UX
      // Make filters sticky at top of viewport but constrained to container width
      filtersElement.style.position = "fixed";
      filtersElement.style.top = "0";
      filtersElement.style.left = "0";
      filtersElement.style.right = "0";
      filtersElement.style.transform = "none";
      filtersElement.style.width = "100%";
      filtersElement.style.maxWidth = "var(--container-width, 1200px)";
      filtersElement.style.margin = "0 auto";
      filtersElement.style.zIndex = "1000";
      isSticky.value = true;
    } else {
      // Reset to normal flow
      filtersElement.style.position = "static";
      filtersElement.style.top = "auto";
      filtersElement.style.left = "auto";
      filtersElement.style.right = "auto";
      filtersElement.style.transform = "none";
      filtersElement.style.width = "auto";
      filtersElement.style.maxWidth = "none";
      filtersElement.style.margin = "";
      filtersElement.style.zIndex = "auto";
      isSticky.value = false;
    }
  };

  window.addEventListener("scroll", onScroll);
  window.addEventListener("resize", () => {
    overviewTop = getOverviewTop();
    onScroll();
  });
  onScroll(); // Call once to set initial state
});
</script>

<style scoped>
.jc-fixed-filters {
  position: static; /* Will be controlled by JavaScript */
  top: 0;
  z-index: 10001 !important;
  background: transparent;
  width: 100%;
}

.jc-fixed-filters-bg {
  background: #fff;
  border-bottom: 1px solid var(--color-cold-gray);
  padding-top: 1rem;
  padding-bottom: 1rem;
  z-index: 10001 !important;
}

.jc-sticky-wrap {
  display: flex;
  align-items: end;
}

.jc-sticky-grid {
  display: grid;
  align-items: end;
  width: 100%;
  min-width: 600px;
  column-gap: 4px !important; /* tighter gap */
  padding-left: 16px !important; /* shift dropdowns slightly right */
  padding-right: 12px; /* space for external add button */
}
.jc-sticky-grid.cols-2 {
  grid-template-columns: 1fr 1fr 1fr; /* label + 2 filters */
}
.jc-sticky-grid.cols-3 {
  grid-template-columns: 1fr 1fr 1fr 1fr; /* label + 3 filters */
}

.jc-right-cell {
  display: flex;
  gap: 12px;
  align-items: end;
  margin-left: 0 !important;
}

.jc-add-link {
  background: none;
  border: none;
  color: var(--color-cold-purple);
  font-weight: 600;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  padding: 0;
  cursor: pointer;
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

/* Button styles removed */

/* Ensure both desktop dropdowns have identical widths (matching the right one) */
.jc-search-filter {
  width: 210px;
  max-width: 100%;
}
.jc-search-filter :deep(.cold-uselectmenu) {
  width: 210px !important;
  min-width: 0 !important;
  max-width: 210px !important;
}
</style>
