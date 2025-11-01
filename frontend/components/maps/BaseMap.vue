<template>
  <!-- Overlay Leaflet Map -->
  <LMap
    ref="map"
    :zoom="zoom"
    :center="center"
    :use-global-leaflet="false"
    :options="mapOptions"
  >
    <div id="info-control" class="info">
      <h2>Answer Coverage</h2>
    </div>
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
import { useCoveredCountries } from "@/composables/useCoveredCountries";

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

const { data: geoJsonData } = useGeoJsonData();
const { data: coveredCountries } = useCoveredCountries();

const isDataReady = computed(
  () =>
    geoJsonData.value &&
    coveredCountries.value &&
    coveredCountries.value.size > 0,
);

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
  const isCovered =
    coveredCountries.value?.has(isoCode?.toLowerCase()) || false;

  const defaultStyle = {
    fillColor: isCovered
      ? "var(--color-cold-purple)"
      : "var(--color-cold-gray)",
    weight: 0.5,
    color: "white",
    fillOpacity: 1,
  };

  const hoverStyle = {
    ...defaultStyle,
    fillOpacity: 0.8,
  };

  layer.setStyle(defaultStyle);

  layer.on("mouseover", () => {
    layer.setStyle(hoverStyle);

    const infoControl = document.getElementById("info-control");
    if (infoControl) {
      infoControl.innerHTML = `
        <h2>${countryName}</h2>
        <h2>${isCovered ? "Data available" : "No data available"}</h2>
      `;
    }
  });

  layer.on("mouseout", () => {
    layer.setStyle(defaultStyle);

    const infoControl = document.getElementById("info-control");
    if (infoControl) {
      infoControl.innerHTML = `
        <h2>Answer Coverage</h2>
      `;
    }
  });

  layer.on("click", () => {
    navigateTo(`/jurisdiction/${isoCode.toLowerCase()}`);
  });
};
</script>
