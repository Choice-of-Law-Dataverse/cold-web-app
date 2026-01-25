<template>
  <div class="base-map-container">
    <!-- Loading State -->
    <div v-if="isLoading" class="map-loading-skeleton" aria-label="Loading map">
      <div class="map-skeleton-shimmer" />
      <span class="sr-only">Loading map data...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="hasError" class="map-error-state" role="alert">
      <UIcon
        name="i-heroicons-exclamation-triangle"
        class="text-red-500"
        size="24"
      />
      <p class="mt-2 text-sm text-gray-600">Unable to load map data</p>
      <button
        class="text-cold-purple mt-1 text-sm hover:underline"
        @click="refetchData"
      >
        Try again
      </button>
    </div>

    <!-- Leaflet Map -->
    <LMap
      v-else
      :zoom="zoom"
      :center="center"
      :use-global-leaflet="false"
      :options="mapOptions"
      class="map-leaflet"
      role="application"
      aria-label="Interactive jurisdiction coverage map"
    >
      <!-- Hover Tooltip -->
      <div
        class="map-tooltip"
        :class="{ 'map-tooltip--visible': hoveredCountry }"
        aria-live="polite"
      >
        <template v-if="hoveredCountry">
          <span class="map-tooltip__name">{{ hoveredCountry.name }}</span>
          <span class="map-tooltip__coverage" :style="hoveredCountry.style">{{
            hoveredCountry.coverage
          }}</span>
        </template>
      </div>

      <!-- SVG Gradient Definition -->
      <svg width="0" height="0" style="position: absolute">
        <defs>
          <linearGradient
            id="map-hover-gradient"
            x1="0%"
            y1="0%"
            x2="100%"
            y2="100%"
          >
            <stop
              offset="0%"
              style="stop-color: var(--color-cold-purple); stop-opacity: 1"
            />
            <stop
              offset="100%"
              style="stop-color: var(--color-cold-green); stop-opacity: 1"
            />
          </linearGradient>
        </defs>
      </svg>

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
        :options="geoJsonOptions"
      />
    </LMap>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { navigateTo } from "#app";
import type {
  LatLngBoundsExpression,
  Layer,
  MapOptions,
  Path,
  PathOptions,
} from "leaflet";

import { useGeoJsonData } from "@/composables/useGeoJsonData";
import { useJurisdictions } from "@/composables/useJurisdictions";

interface GeoJsonFeature {
  properties: {
    iso_a3_eh: string;
    name: string;
  };
}

// Simple tuple types for map coordinates (Leaflet's LatLngTuple includes optional altitude)
type LatLngPair = [number, number];
type BoundsPair = [LatLngPair, LatLngPair];

interface Props {
  zoom?: number;
  center?: LatLngPair;
  enableDragging?: boolean;
  enableScrollWheelZoom?: boolean;
  enableZoomControl?: boolean;
  enableDoubleClickZoom?: boolean;
  backgroundBounds?: BoundsPair;
  maxBounds?: LatLngBoundsExpression | null;
  maxBoundsViscosity?: number;
}

const props = withDefaults(defineProps<Props>(), {
  zoom: 1.5,
  center: () => [35, 0],
  enableDragging: false,
  enableScrollWheelZoom: false,
  enableZoomControl: false,
  enableDoubleClickZoom: false,
  backgroundBounds: () => [
    [-200, -400],
    [200, 400],
  ],
  maxBounds: null,
  maxBoundsViscosity: 1.0,
});

const hoveredCountry = ref<{
  name: string;
  coverage: string;
  style: string;
} | null>(null);

const {
  data: geoJsonData,
  error: geoJsonError,
  isLoading: isGeoJsonLoading,
  refetch: refetchGeoJson,
} = useGeoJsonData();

const {
  data: jurisdictions,
  error: jurisdictionsError,
  isLoading: isJurisdictionsLoading,
  refetch: refetchJurisdictions,
} = useJurisdictions();

const isLoading = computed(
  () => isGeoJsonLoading.value || isJurisdictionsLoading.value,
);

const hasError = computed(
  () => Boolean(geoJsonError.value) || Boolean(jurisdictionsError.value),
);

const isDataReady = computed(
  () =>
    !geoJsonError.value &&
    !jurisdictionsError.value &&
    geoJsonData.value &&
    jurisdictions.value &&
    jurisdictions.value.length > 0,
);

const refetchData = async () => {
  await Promise.all([refetchGeoJson(), refetchJurisdictions()]);
};

// Create a map for quick lookup of answer coverages by ISO code
const answerCoverageMap = computed<Map<string, number>>(() => {
  const coverageMap = new Map<string, number>();
  if (!jurisdictions.value) return coverageMap;

  jurisdictions.value.forEach((jurisdiction) => {
    if (jurisdiction.alpha3Code) {
      coverageMap.set(
        jurisdiction.alpha3Code.toLowerCase(),
        jurisdiction.answerCoverage || 0,
      );
    }
  });
  return coverageMap;
});

const mapOptions = computed<MapOptions>(() => {
  const options: MapOptions = {
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

// Get style for a feature based on coverage data
const getFeatureStyle = (feature: GeoJsonFeature): PathOptions => {
  const isoCode = feature.properties.iso_a3_eh;
  const coverage = answerCoverageMap.value?.get(isoCode?.toLowerCase()) || 0;
  const isCovered = coverage > 0;
  const fillOpacity = isCovered ? 0.25 + (coverage / 100) * 0.75 : 0.25;

  return {
    fillColor: isCovered
      ? "var(--color-cold-purple)"
      : "var(--color-cold-gray)",
    weight: 0.5,
    color: "white",
    fillOpacity,
  };
};

const onEachFeature = (feature: GeoJsonFeature, layer: Layer) => {
  const isoCode = feature.properties.iso_a3_eh;
  const name = feature.properties.name;
  const coverage = answerCoverageMap.value?.get(isoCode?.toLowerCase()) || 0;
  const isCovered = coverage > 0;

  const defaultStyle = getFeatureStyle(feature);
  const hoverStyle: PathOptions = {
    ...defaultStyle,
    fillColor: "url(#map-hover-gradient)",
    fillOpacity: 0.9,
  };

  // Explicitly set initial style (Leaflet's style option may not apply correctly)
  (layer as Path).setStyle(defaultStyle);

  // Add CSS class for transitions after element is available
  layer.on("add", () => {
    const element = (layer as Path).getElement?.();
    if (element) {
      element.classList.add("map-country");
    }
  });

  layer.on("mouseover", () => {
    (layer as Path).setStyle(hoverStyle);
    hoveredCountry.value = {
      name,
      coverage: isCovered
        ? `${coverage.toFixed(1)}% coverage`
        : "No data available",
      style: isCovered ? `color: var(--color-cold-purple);` : `color: #c3c3c3;`,
    };
  });

  layer.on("mouseout", () => {
    (layer as Path).setStyle(defaultStyle);
    hoveredCountry.value = null;
  });

  layer.on("click", () => {
    navigateTo(`/jurisdiction/${isoCode.toLowerCase()}`);
  });
};

const geoJsonOptions = computed(() => ({
  style: getFeatureStyle,
  onEachFeature,
}));
</script>

<style scoped>
.base-map-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.map-leaflet {
  width: 100%;
  height: 100%;
}

/* Loading Skeleton */
.map-loading-skeleton {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  border-radius: 0.5rem;
  overflow: hidden;
}

.map-skeleton-shimmer {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.4) 50%,
    transparent 100%
  );
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* Error State */
.map-error-state {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #fafafa;
  border-radius: 0.5rem;
}

/* Hover Tooltip */
.map-tooltip {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 1000;
  background: white;
  padding: 8px 12px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  opacity: 0;
  transform: translateY(-4px);
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.map-tooltip--visible {
  opacity: 1;
  transform: translateY(0);
}

.map-tooltip__name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-cold-night);
  line-height: 1.3;
}

.map-tooltip__coverage {
  font-size: 0.75rem;
  color: var(--color-cold-purple);
  font-weight: 500;
}

/* Screen reader only */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>

<style>
/* Global styles for Leaflet map countries (CSS transitions) */
.map-country {
  cursor: pointer;
  transition:
    fill-opacity 0.15s ease,
    fill 0.15s ease;
}
</style>
