<template>
  <UCard class="cold-ucard gradient-top-border h-full">
    <div>
      <!-- Map Container -->
      <div
        class="map-container"
        style="height: 600px; width: 100%; margin-top: 0px; position: relative"
      >
        <!-- Dropdown for selecting region -->
        <div class="select-menu-container">
          <USelectMenu
            :model-value="selectedRegion"
            class="w-60"
            placeholder="Select a Region"
            size="xl"
            :items="regionOptions"
            @update:model-value="updateSelectedRegion"
          />
        </div>

        <div v-if="selectedRegion.value === 'Africa'" class="map-wrapper">
          <MapAfrica />
        </div>
        <div v-if="selectedRegion.value === 'All Regions'" class="map-wrapper">
          <MapAllRegions />
        </div>
        <div v-if="selectedRegion.value === 'Arab States'" class="map-wrapper">
          <MapArabStates />
        </div>
        <div
          v-if="selectedRegion.value === 'Asia & Pacific'"
          class="map-wrapper"
        >
          <MapAsiaPacific />
        </div>
        <div v-if="selectedRegion.value === 'Europe'" class="map-wrapper">
          <MapEurope />
        </div>
        <div v-if="selectedRegion.value === 'Middle East'" class="map-wrapper">
          <MapMiddleEast />
        </div>
        <div
          v-if="selectedRegion.value === 'North America'"
          class="map-wrapper"
        >
          <MapNorthAmerica />
        </div>
        <div
          v-if="selectedRegion.value === 'South & Latin America'"
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
        class="text-cold-purple mr-2 shrink-0 cursor-pointer pt-6"
        @click="isDisclaimerVisible = !isDisclaimerVisible"
      />
      <span class="flex-1">
        <ContentRenderer
          v-if="isDisclaimerVisible && disclaimer"
          :value="disclaimer"
          class="inline-block"
        />
      </span>
    </p>
  </UCard>
</template>

<script setup lang="ts">
import { ref } from "vue";

import MapAfrica from "@/components/maps/MapAfrica.vue";
import MapAllRegions from "@/components/maps/MapAllRegions.vue";
import MapArabStates from "@/components/maps/MapArabStates.vue";
import MapAsiaPacific from "@/components/maps/MapAsiaPacific.vue";
import MapEurope from "@/components/maps/MapEurope.vue";
import MapMiddleEast from "@/components/maps/MapMiddleEast.vue";
import MapNorthAmerica from "@/components/maps/MapNorthAmerica.vue";
import MapSouthLatinAmerica from "@/components/maps/MapSouthLatinAmerica.vue";

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
.map-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.map-container {
  overflow: hidden;
}

.select-menu-container {
  position: absolute;
  top: 32px;
  right: 12px;
  z-index: 2000;
}

.select-menu-container .u-select-menu-dropdown {
  z-index: 2001;
}
</style>
