<template>
  <div
    :class="['jc-fixed-filters', '-mb-16', { 'jc-fixed-filters-bg': isSticky }]"
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
  // Sticky background logic
  const el = document.querySelector('.jc-fixed-filters')
  const onScroll = () => {
    if (!el) return
    const { top } = el.getBoundingClientRect()
    isSticky.value = top <= 0
  }
  window.addEventListener('scroll', onScroll)
})
</script>

<style scoped>
.jc-fixed-filters {
  position: sticky;
  top: 0;
  z-index: 10000;
  background: transparent;
  padding-top: 1em;
}
.jc-fixed-filters-bg {
  background: #fff;
}
.jc-sticky-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 0 1.5rem;
  align-items: end;
}
.jc-sticky-grid > div {
  /* Ensures SearchFilters fill their columns */
  min-width: 0;
}
</style>
