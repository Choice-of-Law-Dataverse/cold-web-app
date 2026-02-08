<template>
  <UCard :ui="{ body: '!p-0' }">
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
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { defineAsyncComponent, h, ref } from "vue";

// Loading placeholder for async map components
const MapLoadingPlaceholder = {
  render() {
    return h("div", { class: "map-async-loading" }, [
      h("div", { class: "map-async-loading__spinner" }),
    ]);
  },
};

// Error placeholder for failed async map loads
const MapErrorPlaceholder = {
  render() {
    return h("div", { class: "map-async-error" }, [
      h("span", "Failed to load map"),
    ]);
  },
};

// Async component options with loading/error handlers
const asyncComponentOptions = {
  loadingComponent: MapLoadingPlaceholder,
  errorComponent: MapErrorPlaceholder,
  delay: 100,
  timeout: 10000,
};

// Lazy load regional map components for better performance
const MapAfrica = defineAsyncComponent({
  loader: () => import("@/components/maps/MapAfrica.vue"),
  ...asyncComponentOptions,
});
const MapAllRegions = defineAsyncComponent({
  loader: () => import("@/components/maps/MapAllRegions.vue"),
  ...asyncComponentOptions,
});
const MapArabStates = defineAsyncComponent({
  loader: () => import("@/components/maps/MapArabStates.vue"),
  ...asyncComponentOptions,
});
const MapAsiaPacific = defineAsyncComponent({
  loader: () => import("@/components/maps/MapAsiaPacific.vue"),
  ...asyncComponentOptions,
});
const MapEurope = defineAsyncComponent({
  loader: () => import("@/components/maps/MapEurope.vue"),
  ...asyncComponentOptions,
});
const MapMiddleEast = defineAsyncComponent({
  loader: () => import("@/components/maps/MapMiddleEast.vue"),
  ...asyncComponentOptions,
});
const MapNorthAmerica = defineAsyncComponent({
  loader: () => import("@/components/maps/MapNorthAmerica.vue"),
  ...asyncComponentOptions,
});
const MapSouthLatinAmerica = defineAsyncComponent({
  loader: () => import("@/components/maps/MapSouthLatinAmerica.vue"),
  ...asyncComponentOptions,
});

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

/* Map Transition */
.map-fade-enter-active,
.map-fade-leave-active {
  transition: opacity 0.2s ease;
}

.map-fade-enter-from,
.map-fade-leave-to {
  opacity: 0;
}

/* Async Component Loading State */
.map-async-loading {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
}

.map-async-loading__spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-cold-gray);
  border-top-color: var(--color-cold-purple);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Async Component Error State */
.map-async-error {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fef2f2;
  color: #991b1b;
  font-size: 0.875rem;
}
</style>
