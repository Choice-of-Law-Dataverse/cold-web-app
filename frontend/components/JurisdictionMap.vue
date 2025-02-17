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
            class="w-12 lg:w-60"
            placeholder="Select a Region"
            size="xl"
            :options="regionOptions"
          />
        </div>

        <div v-if="selectedRegion === 'Africa'" class="map-wrapper">
          <MapAfrica />
        </div>
        <div v-if="selectedRegion === 'All Regions'" class="map-wrapper">
          <MapAllRegions />
        </div>
        <div v-if="selectedRegion === 'Arab States'" class="map-wrapper">
          <MapArabStates />
        </div>
        <div v-if="selectedRegion === 'Asia & Pacific'" class="map-wrapper">
          <MapAsiaPacific />
        </div>
        <div v-if="selectedRegion === 'Europe'" class="map-wrapper">
          <MapEurope />
        </div>
        <div v-if="selectedRegion === 'Middle East'" class="map-wrapper">
          <MapMiddleEast />
        </div>
        <div v-if="selectedRegion === 'North America'" class="map-wrapper">
          <MapNorthAmerica />
        </div>
        <div
          v-if="selectedRegion === 'South & Latin America'"
          class="map-wrapper"
        >
          <MapSouthLatinAmerica />
        </div>
      </div>
    </div>
    <p
      class="result-value-small flex items-start"
      style="
        margin: 0px 0px -14px -12px !important;
        font-size: 12px !important;
        line-height: 24px !important;
      "
    >
      <UIcon
        name="i-material-symbols:info-outline"
        size="18"
        class="text-cold-purple mr-2 flex-shrink-0 pt-6 cursor-pointer"
        @click="isDisclaimerVisible = !isDisclaimerVisible"
      />
      <span class="flex-1">
        <ContentDoc
          v-if="isDisclaimerVisible"
          path="/map_disclaimer"
          class="inline-block"
        />
      </span>
    </p>
  </UCard>
</template>

<script setup>
import { ref } from 'vue'

import MapAfrica from './Maps/MapAfrica.vue'
import MapAllRegions from './Maps/MapAllRegions.vue'
import MapArabStates from './Maps/MapArabStates.vue'
import MapAsiaPacific from './Maps/MapAsiaPacific.vue'
import MapEurope from './Maps/MapEurope.vue'
import MapMiddleEast from './Maps/MapMiddleEast.vue'
import MapNorthAmerica from './Maps/MapNorthAmerica.vue'
import MapSouthLatinAmerica from './Maps/MapSouthLatinAmerica.vue'

// Reactive property to track the selected region
const selectedRegion = ref('All Regions')

const updateSelectedRegion = (option) => {
  selectedRegion.value = option.value // Extract the `value` field
}

// Options for the USelectMenu
const regionOptions = [
  { label: 'All Regions', value: 'All Regions' },
  { label: 'Africa', value: 'Africa' },
  { label: 'Arab States', value: 'Arab States' },
  { label: 'Asia & Pacific', value: 'Asia & Pacific' },
  { label: 'Europe', value: 'Europe' },
  { label: 'Middle East', value: 'Middle East' },
  { label: 'North America', value: 'North America' },
  { label: 'South & Latin America', value: 'South & Latin America' },
]

const isDisclaimerVisible = ref(false)
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
  top: 12px; /* Adjust as needed */
  right: 12px; /* Adjust as needed */
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
