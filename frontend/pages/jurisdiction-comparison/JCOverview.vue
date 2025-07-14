<template>
  <div>
    <div class="jc-grid jc-overview-row">
      <div class="jc-col-1">
        <h2 class="mt-8 mb-6">Overview</h2>
      </div>
      <div class="jc-col-2 mt-6 mb-6">
        <SearchFilters
          :options="jurisdictionOptions"
          v-model="currentJurisdictionFilter"
          class="jc-search-filter"
          showAvatars="true"
          :multiple="false"
        />
      </div>
      <div class="jc-col-3 mt-6 mb-6">
        <SearchFilters
          :options="jurisdictionOptions"
          v-model="currentJurisdictionFilter"
          class="jc-search-filter"
          showAvatars="true"
          :multiple="false"
        />
      </div>
      <div class="jc-col-4 mt-6 mb-6">
        <SearchFilters
          :options="jurisdictionOptions"
          v-model="currentJurisdictionFilter"
          class="jc-search-filter"
          showAvatars="true"
          :multiple="false"
        />
      </div>
    </div>
    <hr class="jc-hr" />
    <div class="jc-grid jc-data-row">
      <div class="jc-col-1 jc-empty"></div>
      <div class="jc-col-2">
        <div class="result-value-medium">
          <p>Civil Law</p>
          <br />
          <p>44 court decisions</p>
          <br />
          <p>1 domestic instrument</p>
          <br />
          <p>0 arbitration laws</p>
        </div>
      </div>
      <div class="jc-col-3">
        <div class="result-value-medium">
          <p>Civil Law</p>
          <br />
          <p>44 court decisions</p>
          <br />
          <p>1 domestic instrument</p>
          <br />
          <p>0 arbitration laws</p>
        </div>
      </div>
      <div class="jc-col-4">
        <div class="result-value-medium">
          <p>Civil Law</p>
          <br />
          <p>44 court decisions</p>
          <br />
          <p>1 domestic instrument</p>
          <br />
          <p>0 arbitration laws</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import SearchFilters from '@/components/search-results/SearchFilters.vue'

// Initialize jurisdiction options with default value
const jurisdictionOptions = ref([{ label: 'All Jurisdictions' }])
const currentJurisdictionFilter = ref([])

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
})
</script>

<style scoped>
.jc-grid {
  display: grid;
  grid-template-columns: 0.75fr 1fr 1fr 1fr;
  align-items: start;
  gap: 0 1.5rem;
}

.jc-overview-row {
  margin-bottom: 0;
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

.jc-hr {
  border-top: 1px solid var(--color-cold-gray);
}

.result-value-medium {
  font-weight: 400 !important;
  margin-top: 32px !important;
}

.jc-search-filter :deep(.cold-uselectmenu) {
  width: 100% !important;
}
</style>
