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
      ref="mapRef"
      :zoom="zoom"
      :center="center"
      :use-global-leaflet="false"
      :options="mapOptions"
      class="map-leaflet"
      role="application"
      aria-label="Interactive jurisdiction coverage map"
    >
      <!-- Tile Layer -->
      <LTileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        :attribution="'&copy; OpenStreetMap contributors'"
        :max-zoom="19"
      />

      <!-- White Background - Extended to cover larger area for dragging -->
      <LRectangle
        :bounds="backgroundBounds as [LatLngTuple, LatLngTuple]"
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
  Map as LeafletMap,
  MapOptions,
} from "leaflet";

import { useGeoJsonData } from "@/composables/useGeoJsonData";
import { useJurisdictions } from "@/composables/useJurisdictions";

interface GeoJsonFeature {
  properties: {
    iso_a3_eh: string;
    name: string;
  };
}

type LatLngTuple = [number, number];

interface Props {
  zoom?: number;
  center?: LatLngTuple;
  enableDragging?: boolean;
  enableScrollWheelZoom?: boolean;
  enableZoomControl?: boolean;
  enableDoubleClickZoom?: boolean;
  backgroundBounds?: LatLngBoundsExpression;
  maxBounds?: LatLngBoundsExpression | null;
  maxBoundsViscosity?: number;
}

const props = withDefaults(defineProps<Props>(), {
  zoom: 1.5,
  center: () => [35, 0] as LatLngTuple,
  enableDragging: false,
  enableScrollWheelZoom: false,
  enableZoomControl: false,
  enableDoubleClickZoom: false,
  backgroundBounds: () =>
    [
      [-200, -400],
      [200, 400],
    ] as LatLngBoundsExpression,
  maxBounds: null,
  maxBoundsViscosity: 1.0,
});

const mapRef = ref<{ leafletObject: LeafletMap } | null>(null);

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

const refetchData = () => {
  refetchGeoJson();
  refetchJurisdictions();
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

// Style function for initial render (prevents flash of default Leaflet styles)
const getFeatureStyle = (feature: GeoJsonFeature) => {
  const isoCode = feature.properties.iso_a3_eh;
  const answerCoverage =
    answerCoverageMap.value?.get(isoCode?.toLowerCase()) || 0;
  const isCovered = answerCoverage > 0;
  const fillOpacity = isCovered ? 0.1 + (answerCoverage / 100) * 0.9 : 1;

  return {
    fillColor: isCovered
      ? "var(--color-cold-purple)"
      : "var(--color-cold-gray)",
    weight: 0.5,
    color: "white",
    fillOpacity,
    className: "map-country",
  };
};

const onEachFeature = (feature: GeoJsonFeature, layer: Layer) => {
  const isoCode = feature.properties.iso_a3_eh;
  const answerCoverage =
    answerCoverageMap.value?.get(isoCode?.toLowerCase()) || 0;
  const isCovered = answerCoverage > 0;
  const fillOpacity = isCovered ? 0.1 + (answerCoverage / 100) * 0.9 : 1;

  const defaultStyle = getFeatureStyle(feature);
  const hoverStyle = {
    ...defaultStyle,
    fillColor: "var(--color-cold-teal)",
    fillOpacity: Math.max(0.8, fillOpacity),
  };

  layer.on("mouseover", () => {
    // @ts-expect-error Leaflet layer type
    layer.setStyle(hoverStyle);
  });

  layer.on("mouseout", () => {
    // @ts-expect-error Leaflet layer type
    layer.setStyle(defaultStyle);
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
