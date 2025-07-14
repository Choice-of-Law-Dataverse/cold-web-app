<template>
  <div>
    <div class="jc-grid jc-overview-row">
      <div class="jc-col-1">
        <h2 class="mt-8 mb-6">Overview</h2>
      </div>
      <div class="jc-col-2">
        <SearchFilters
          :options="jurisdictionOptions"
          v-model="currentJurisdictionFilter"
          class="w-full"
          showAvatars="true"
        />
      </div>
      <div class="jc-col-3 jc-empty"></div>
      <div class="jc-col-4 jc-empty"></div>
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
import { ref } from 'vue'
import SearchFilters from '@/components/search-results/SearchFilters.vue'

// Initialize jurisdiction options with default value
const jurisdictionOptions = ref([{ label: 'All Jurisdictions' }])
const currentJurisdictionFilter = ref([])
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
</style>
