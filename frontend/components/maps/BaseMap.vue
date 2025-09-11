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
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  zoom: {
    type: Number,
    default: 1.5
  },
  center: {
    type: Array,
    default: () => [35, 0]
  },
  enableDragging: {
    type: Boolean,
    default: false
  },
  enableScrollWheelZoom: {
    type: Boolean,
    default: false
  },
  enableZoomControl: {
    type: Boolean,
    default: false
  },
  enableDoubleClickZoom: {
    type: Boolean,
    default: false
  },
  backgroundBounds: {
    type: Array,
    default: () => [[-200, -400], [200, 400]]
  },
  maxBounds: {
    type: Array,
    default: null
  },
  maxBoundsViscosity: {
    type: Number,
    default: 1.0
  }
})

// Import the new composables
const { data: geoJsonData } = useGeoJsonData()
const { data: coveredCountries } = useCoveredCountries()

// Data readiness state
const isDataReady = computed(
  () =>
    geoJsonData.value &&
    coveredCountries.value &&
    coveredCountries.value.size > 0
)

// Map options computed from props
const mapOptions = computed(() => {
  const options = {
    zoomControl: props.enableZoomControl,
    scrollWheelZoom: props.enableScrollWheelZoom,
    attributionControl: false,
    dragging: props.enableDragging,
    doubleClickZoom: props.enableDoubleClickZoom,
  }

  // Add maxBounds if provided
  if (props.maxBounds) {
    options.maxBounds = props.maxBounds
    options.maxBoundsViscosity = props.maxBoundsViscosity
  }

  return options
})

// Example function for handling GeoJSON features
const onEachFeature = (feature, layer) => {
  const isoCode = feature.properties.iso_a3_eh // Get the ISO3 code
  const countryName = feature.properties.name // Get the country's name
  const isCovered = coveredCountries.value?.has(isoCode?.toLowerCase()) || false

  // Default style
  const defaultStyle = {
    fillColor: isCovered
      ? 'var(--color-cold-purple)'
      : 'var(--color-cold-gray)',
    weight: 0.5,
    color: 'white',
    fillOpacity: 1,
  }

  // Hover style
  const hoverStyle = {
    ...defaultStyle,
    fillOpacity: 0.8, // 80% alpha on hover
  }

  // Set default style
  layer.setStyle(defaultStyle)

  // Add hover events
  layer.on('mouseover', () => {
    layer.setStyle(hoverStyle)

    // Update the info control
    const infoControl = document.getElementById('info-control')
    if (infoControl) {
      infoControl.innerHTML = `
        <h2>${countryName}</h2>
        <h2>${isCovered ? 'Data available' : 'No data available'}</h2>
      `
    }
  })

  layer.on('mouseout', () => {
    layer.setStyle(defaultStyle)

    // Reset the info control
    const infoControl = document.getElementById('info-control')
    if (infoControl) {
      infoControl.innerHTML = `
        <h2>Answer Coverage</h2>
      `
    }
  })

  // Add a click event to navigate to the country-specific URL
  layer.on('click', () => {
    navigateTo(`/jurisdiction/${isoCode.toLowerCase()}`)
  })
}
</script>