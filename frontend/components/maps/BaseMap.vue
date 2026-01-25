<template>
  <!-- Overlay Leaflet Map -->
  <LMap
    ref="map"
    :zoom="zoom"
    :center="center"
    :use-global-leaflet="false"
    :options="mapOptions"
  >
    <div id="info-control" class="info" />
    <!-- Tile Layer -->
    <LTileLayer
      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      :attribution="'&copy; OpenStreetMap contributors'"
      :max-zoom="19"
    />
    <!-- White Background - Extended to cover larger area for dragging -->
    <LRectangle
      :bounds="backgroundBounds"
      :fill="true"
      color="white"
      :weight="0"
      :fill-opacity="1"
    />
    <!-- GeoJSON Layer -->
    <LGeoJson
      v-if="isDataReady"
      :geojson="geoJsonData"
      :options="{ onEachFeature }"
    />
  </LMap>
</template>

<script setup>
import { computed } from "vue";
import { navigateTo } from "#app";

import { useGeoJsonData } from "@/composables/useGeoJsonData";
import { useJurisdictions } from "@/composables/useJurisdictions";

const props = defineProps({
  zoom: {
    type: Number,
    default: 1.5,
  },
  center: {
    type: Array,
    default: () => [35, 0],
  },
  enableDragging: {
    type: Boolean,
    default: false,
  },
  enableScrollWheelZoom: {
    type: Boolean,
    default: false,
  },
  enableZoomControl: {
    type: Boolean,
    default: false,
  },
  enableDoubleClickZoom: {
    type: Boolean,
    default: false,
  },
  backgroundBounds: {
    type: Array,
    default: () => [
      [-200, -400],
      [200, 400],
    ],
  },
  maxBounds: {
    type: Array,
    default: null,
  },
  maxBoundsViscosity: {
    type: Number,
    default: 1.0,
  },
});

const { data: geoJsonData, error: geoJsonError } = useGeoJsonData();
const { data: jurisdictions, error: jurisdictionsError } = useJurisdictions();

const isDataReady = computed(
  () =>
    !geoJsonError.value &&
    !jurisdictionsError.value &&
    geoJsonData.value &&
    jurisdictions.value &&
    jurisdictions.value.length > 0,
);

// Create a map for quick lookup of answer coverages by ISO code
const answerCoverageMap = computed(() => {
  if (!jurisdictions.value) return new Map();

  const map = new Map();
  jurisdictions.value.forEach((jurisdiction) => {
    if (jurisdiction.alpha3Code) {
      map.set(
        jurisdiction.alpha3Code.toLowerCase(),
        jurisdiction.answerCoverage || 0,
      );
    }
  });
  return map;
});

const mapOptions = computed(() => {
  const options = {
    zoomControl: props.enableZoomControl,
    scrollWheelZoom: props.enableScrollWheelZoom,
    attributionControl: false,
    dragging: props.enableDragging,
    doubleClickZoom: props.enableDoubleClickZoom,
  };

  if (props.maxBounds) {
    options.maxBounds = props.maxBounds;
    options.maxBoundsViscosity = props.maxBoundsViscosity;
  }

  return options;
});

const onEachFeature = (feature, layer) => {
  const isoCode = feature.properties.iso_a3_eh;
  const countryName = feature.properties.name;
  const answerCoverage =
    answerCoverageMap.value?.get(isoCode?.toLowerCase()) || 0;
  const isCovered = answerCoverage > 0;

  // Calculate opacity based on answer coverage (0-100 maps to 0.1-1.0)
  const fillOpacity = isCovered ? 0.1 + (answerCoverage / 100) * 0.9 : 1;

  const defaultStyle = {
    fillColor: isCovered
      ? "var(--color-cold-purple)"
      : "var(--color-cold-gray)",
    weight: 0.5,
    color: "white",
    fillOpacity,
  };

  const hoverStyle = {
    ...defaultStyle,
    fillColor: "var(--color-cold-teal)",
    fillOpacity: Math.max(0.8, fillOpacity),
  };

  layer.setStyle(defaultStyle);

  layer.on("mouseover", () => {
    layer.setStyle(hoverStyle);

    const infoControl = document.getElementById("info-control");
    if (infoControl) {
      const displayText = isCovered
        ? `${answerCoverage.toFixed(1)}%`
        : "No data available";
      infoControl.innerHTML = `
        <h2 class="text-[var(--color-cold-night)]">${countryName}</h2>
        <h4>${displayText}</h4>
      `;
    }
  });

  layer.on("mouseout", () => {
    layer.setStyle(defaultStyle);

    const infoControl = document.getElementById("info-control");
    if (infoControl) {
      infoControl.innerHTML = "";
    }
  });

  layer.on("click", () => {
    navigateTo(`/jurisdiction/${isoCode.toLowerCase()}`);
  });
};
</script>
