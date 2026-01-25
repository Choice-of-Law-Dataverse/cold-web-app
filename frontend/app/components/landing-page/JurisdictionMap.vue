<template>
  <UCard class="cold-ucard overflow-hidden" :ui="{ body: '!p-0' }">
    <div class="gradient-top-border" />
    <div class="p-4 sm:p-6">
      <!-- Map Container -->
      <div class="map-container">
        <!-- Dropdown for selecting region -->
        <div class="select-menu-container">
          <USelectMenu
            :model-value="selectedRegion"
            class="w-60"
            placeholder="Select a Region"
            size="xl"
            :items="regionOptions"
            aria-label="Select map region"
            @update:model-value="updateSelectedRegion"
          />
        </div>

        <!-- Color Legend -->
        <div class="map-legend" aria-label="Map coverage legend">
          <div class="map-legend__item">
            <span class="map-legend__color map-legend__color--covered" />
            <span class="map-legend__label">Data available</span>
          </div>
          <div class="map-legend__item">
            <span class="map-legend__color map-legend__color--none" />
            <span class="map-legend__label">No data</span>
          </div>
        </div>

        <!-- Regional Map Components with Transition -->
        <Transition name="map-fade" mode="out-in">
          <div
            v-if="selectedRegion.value === 'Africa'"
            :key="'africa'"
            class="map-wrapper"
          >
            <MapAfrica />
          </div>
          <div
            v-else-if="selectedRegion.value === 'All Regions'"
            :key="'all'"
            class="map-wrapper"
          >
            <MapAllRegions />
          </div>
          <div
            v-else-if="selectedRegion.value === 'Arab States'"
            :key="'arab'"
            class="map-wrapper"
          >
            <MapArabStates />
          </div>
          <div
            v-else-if="selectedRegion.value === 'Asia & Pacific'"
            :key="'asia'"
            class="map-wrapper"
          >
            <MapAsiaPacific />
          </div>
          <div
            v-else-if="selectedRegion.value === 'Europe'"
            :key="'europe'"
            class="map-wrapper"
          >
            <MapEurope />
          </div>
          <div
            v-else-if="selectedRegion.value === 'Middle East'"
            :key="'middle-east'"
            class="map-wrapper"
          >
            <MapMiddleEast />
          </div>
          <div
            v-else-if="selectedRegion.value === 'North America'"
            :key="'north-america'"
            class="map-wrapper"
          >
            <MapNorthAmerica />
          </div>
          <div
            v-else-if="selectedRegion.value === 'South & Latin America'"
            :key="'south-latin'"
            class="map-wrapper"
          >
            <MapSouthLatinAmerica />
          </div>
        </Transition>
      </div>

      <!-- Disclaimer -->
      <p class="result-value-small mt-4 flex items-start text-xs">
        <UIcon
          name="i-material-symbols:info-outline"
          size="18"
          class="text-cold-purple mr-2 shrink-0 cursor-pointer"
          role="button"
          tabindex="0"
          aria-label="Toggle disclaimer"
          @click="isDisclaimerVisible = !isDisclaimerVisible"
          @keydown.enter="isDisclaimerVisible = !isDisclaimerVisible"
          @keydown.space.prevent="isDisclaimerVisible = !isDisclaimerVisible"
        />
        <span class="flex-1">
          <Transition name="fade">
            <ContentRenderer
              v-if="isDisclaimerVisible && disclaimer"
              :value="disclaimer"
              class="inline-block"
            />
          </Transition>
        </span>
      </p>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref } from "vue";

// Lazy load regional map components for better performance
const MapAfrica = defineAsyncComponent(
  () => import("@/components/maps/MapAfrica.vue"),
);
const MapAllRegions = defineAsyncComponent(
  () => import("@/components/maps/MapAllRegions.vue"),
);
const MapArabStates = defineAsyncComponent(
  () => import("@/components/maps/MapArabStates.vue"),
);
const MapAsiaPacific = defineAsyncComponent(
  () => import("@/components/maps/MapAsiaPacific.vue"),
);
const MapEurope = defineAsyncComponent(
  () => import("@/components/maps/MapEurope.vue"),
);
const MapMiddleEast = defineAsyncComponent(
  () => import("@/components/maps/MapMiddleEast.vue"),
);
const MapNorthAmerica = defineAsyncComponent(
  () => import("@/components/maps/MapNorthAmerica.vue"),
);
const MapSouthLatinAmerica = defineAsyncComponent(
  () => import("@/components/maps/MapSouthLatinAmerica.vue"),
);

interface RegionOption {
  label: string;
  value: string;
}

const regionOptions: RegionOption[] = [
  { label: "All Regions", value: "All Regions" },
  { label: "Africa", value: "Africa" },
  { label: "Arab States", value: "Arab States" },
  { label: "Asia & Pacific", value: "Asia & Pacific" },
  { label: "Europe", value: "Europe" },
  { label: "Middle East", value: "Middle East" },
  { label: "North America", value: "North America" },
  { label: "South & Latin America", value: "South & Latin America" },
];

const selectedRegion = ref<RegionOption>(
  regionOptions[0] ?? { label: "All Regions", value: "All Regions" },
);

const updateSelectedRegion = (option: RegionOption) => {
  selectedRegion.value = option;
};

const isDisclaimerVisible = ref(false);

const { data: disclaimer } = await useAsyncData("map_disclaimer", () =>
  queryCollection("content").path("/map_disclaimer").first(),
);
</script>

<style scoped>
.map-container {
  height: 600px;
  width: 100%;
  position: relative;
  overflow: hidden;
}

@media (max-width: 640px) {
  .map-container {
    height: 400px;
  }
}

.map-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.select-menu-container {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2000;
}

.select-menu-container .u-select-menu-dropdown {
  z-index: 2001;
}

/* Color Legend */
.map-legend {
  position: absolute;
  bottom: 16px;
  left: 12px;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(4px);
  padding: 8px 12px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.map-legend__item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.map-legend__color {
  width: 16px;
  height: 12px;
  border-radius: 2px;
  flex-shrink: 0;
}

.map-legend__color--covered {
  background: var(--color-cold-purple);
  opacity: 0.7;
}

.map-legend__color--none {
  background: var(--color-cold-gray);
}

.map-legend__label {
  font-size: 0.6875rem;
  color: var(--color-cold-night);
  line-height: 1;
}

/* Map Transition */
.map-fade-enter-active,
.map-fade-leave-active {
  transition: opacity 0.2s ease;
}

.map-fade-enter-from,
.map-fade-leave-to {
  opacity: 0;
}

/* Disclaimer Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
