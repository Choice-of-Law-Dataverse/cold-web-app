<template>
  <UCard class="cold-ucard">
    <div>
      <!-- Map Container -->
      <div
        style="height: 600px; width: 100%; margin-top: 0px; position: relative"
      >
        <!-- Dropdown for selecting region -->
        <div class="select-menu-container">
          <USelectMenu
            :model-value="selectedRegion"
            @update:modelValue="updateSelectedRegion"
            class="w-72 lg:w-96"
            placeholder="Select a Region"
            size="xl"
            :options="regionOptions"
          />
        </div>

        <!-- All Regions Map -->
        <div v-if="selectedRegion === 'all'" class="map-wrapper">
          <MapAllRegions />
        </div>

        <!-- Europe Map -->
        <div v-if="selectedRegion === 'europe'" class="map-wrapper">
          <MapEurope />
        </div>

        <!-- North America Map -->
        <div v-if="selectedRegion === 'n-america'" class="map-wrapper">
          <MapNorthAmerica />
        </div>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { ref } from 'vue'

import MapAllRegions from './Maps/MapAllRegions.vue'
import MapEurope from './Maps/MapEurope.vue'
import MapNorthAmerica from './Maps/MapNorthAmerica.vue'

// Reactive property to track the selected region
const selectedRegion = ref('all')

const updateSelectedRegion = (option) => {
  selectedRegion.value = option.value // Extract the `value` field
}

// Options for the USelectMenu
const regionOptions = [
  { label: 'All Regions', value: 'all' },
  { label: 'Europe', value: 'europe' },
  { label: 'North America', value: 'n-america' },
]
</script>

<style scoped>
/* Ensure maps occupy the same space */
.map-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.select-menu-container {
  position: absolute;
  top: 10px; /* Adjust as needed */
  right: 10px; /* Adjust as needed */
  z-index: 1000; /* Ensure it appears above the map */
}

/* Ensure the dropdown menu appears correctly */
.select-menu-container .u-select-menu-dropdown {
  z-index: 1100; /* Higher than the container for the dropdown */
}

/* Hide inactive maps */
/* .map-wrapper:not([v-show]) {
  display: none;
} */
/* .select-menu-container { */
/* position: relative; Ensure it's positioned relative to control stacking */
/* z-index: 1000; High enough to appear above the map */
/* margin-bottom: -40px; Adjust spacing between the menu and map */
/* } */
</style>
