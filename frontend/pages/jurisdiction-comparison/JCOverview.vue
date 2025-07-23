<template>
  <div>
    <div class="hidden md:block">
      <!-- <h2 class="mt-8 mb-6 mr-[106px] jc-z-top">asd</h2> -->
      <div class="mt-24 jc-z-top"></div>
      <hr class="jc-hr" />
      <div class="jc-grid jc-data-row">
        <div class="jc-col-1 jc-empty"></div>
        <div
          v-for="index in 3"
          :key="`desktop-data-${index}`"
          :class="`jc-col-${index + 1}`"
        >
          <div class="result-value-medium">
            <p
              v-for="(line, lineIndex) in sampleData"
              :key="lineIndex"
              class="pt-8"
            >
              {{ line }}
              <br v-if="lineIndex < sampleData.length - 1" />
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile & Tablet Layout -->
    <div class="md:hidden">
      <div class="mobile-layout">
        <!-- Data cards -->
        <div class="data-cards">
          <h2 class="mt-4">Overview</h2>
          <div
            v-for="(filter, index) in jurisdictionFilters"
            :key="`mobile-data-${index}`"
            class="data-card"
          >
            <h3 class="data-card-title flex items-center">
              <template
                v-if="
                  filter.value.value.length > 0 &&
                  filter.value.value[0]?.label !== 'All Jurisdictions'
                "
              >
                <img
                  v-if="
                    !erroredFlags[index] &&
                    getFlagUrl(filter.value.value[0].label)
                  "
                  :src="getFlagUrl(filter.value.value[0].label)"
                  @error="() => (erroredFlags[index] = true)"
                  style="
                    height: 18px;
                    width: auto;
                    margin-right: 0.5em;
                    border-radius: 0;
                    border: 1px solid var(--color-cold-gray);
                  "
                  :alt="filter.value.value[0].label + ' flag'"
                />
                {{ filter.value.value[0].label }}
              </template>
              <template v-else>
                {{ `Jurisdiction ${index + 1}` }}
              </template>
            </h3>
            <div>
              <p
                v-for="(line, lineIndex) in sampleData"
                :key="lineIndex"
                class="data-line"
              >
                {{ line }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useJurisdictionComparison } from '@/composables/useJurisdictionComparison'

// Use shared jurisdiction comparison state
const {
  jurisdictionOptions,
  jurisdictionFilters,
  selectedJurisdictionCodes,
  loadJurisdictions,
} = useJurisdictionComparison()

// Dynamic sample data based on selected jurisdictions
const sampleData = computed(() => {
  const codes = selectedJurisdictionCodes.value
  return [
    codes[0] || 'Civil Law', // Replace 'Civil Law' with ISO3 code
    '44 court decisions',
    '1 domestic instrument',
    '0 arbitration laws',
  ]
})

// --- Flag logic ---
import { reactive } from 'vue'
const erroredFlags = reactive({})
function getFlagUrl(label) {
  if (!label || label === 'All Jurisdictions') return ''
  // Use Alpha-3 code if available in jurisdictionOptions
  const found = jurisdictionOptions.value.find((j) => j.label === label)
  if (found && found.avatar) return found.avatar
  // Fallback: try to use label as ISO code (lowercase)
  return `https://choiceoflawdataverse.blob.core.windows.net/assets/flags/${label.toLowerCase()}.svg`
}

// Initialization
onMounted(async () => {
  await loadJurisdictions()
})
</script>

<style scoped>
/* Desktop Grid Layout */

.jc-grid,
.jc-data-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  align-items: start;
  gap: 0 1.5rem;
}

.jc-overview-row {
  margin-bottom: 0;
  position: sticky;
  top: 0;
  /* z-index: 10; */
  background: #fff;
}

.jc-data-row {
  margin-top: 0;
}

.jc-col-1 {
  grid-column: 1;
}
.jc-col-2 {
  grid-column: 2;
}
.jc-col-3 {
  grid-column: 3;
}
.jc-col-4 {
  grid-column: 4;
}

/* Shared scrollbar styles */
.jc-mobile-filters-container,
.jc-mobile-data-container {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  padding: 1rem 0;
  scrollbar-width: thin;
  scrollbar-color: var(--color-cold-gray) transparent;
}

.jc-mobile-filters-container::-webkit-scrollbar,
.jc-mobile-data-container::-webkit-scrollbar {
  height: 6px;
}

/* Mobile & Tablet Layout */
.mobile-layout {
  padding: 0.25rem;
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

/* Data cards for mobile */
.data-cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .data-cards {
    grid-template-columns: repeat(3, 1fr);
  }
}

.data-card {
  padding-top: 2rem;
}

.data-card-title {
  font-weight: 600;
  font-size: 1.125rem;
  margin-bottom: 1rem;
  color: var(--color-cold-purple);
}

.data-line {
  margin-bottom: 0.5rem;
  /* color: #374151; */
  line-height: 2;
}

.result-value-medium {
  font-weight: 400 !important;
  margin-top: 32px !important;
}

/* Search filter styling */
.jc-search-filter {
  width: 240px;
  max-width: 100%;
}
.jc-search-filter :deep(.cold-uselectmenu) {
  width: 240px !important;
  min-width: 0 !important;
  max-width: 240px !important;
}

/* Highest z-index for Overview heading */
.jc-z-top {
  position: relative;
  /* z-index: 9999; */
  pointer-events: none;
}
</style>
