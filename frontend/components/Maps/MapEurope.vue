<template>
  <div id="map-container-all" style="height: 100%">
    <!-- Overlay Leaflet Map -->
    <LMap
      :key="mapKey"
      ref="map"
      :zoom="zoom"
      :center="center"
      :use-global-leaflet="false"
      :options="{
        zoomControl: false,
        scrollWheelZoom: false,
        attributionControl: false,
        dragging: false,
        doubleClickZoom: false,
      }"
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
      <!-- White Background -->
      <LRectangle
        :bounds="[
          [-120, 200],
          [90, -200],
        ]"
        :fill="true"
        color="white"
        weight="0"
        fill-opacity="1"
      />
      <!-- GeoJSON Layer -->
      <LGeoJson
        v-if="isDataReady"
        :geojson="geoJsonData"
        :options="{ onEachFeature }"
      />
    </LMap>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

defineProps({
  zoom: Number,
  center: Array,
})

const mapKey = ref(Date.now()) // Use a unique timestamp as key

// Map configuration
const zoom = ref(4)
const center = ref([55, 18])

// GeoJSON data and readiness state
const geoJsonData = ref(null)
const coveredCountries = ref([]) // Example: Country coverage data
const isDataReady = computed(
  () => geoJsonData.value && coveredCountries.value.length > 0
)

// Example function for handling GeoJSON features
const onEachFeature = (feature, layer) => {
  const isoCode = feature.properties.adm0_a3 // Get the ISO3 code
  const countryName = feature.properties.name // Get the country's name
  const isCovered = coveredCountries.value.includes(isoCode)

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
  })

  layer.on('mouseout', () => {
    layer.setStyle(defaultStyle)
  })

  // Add a click event to navigate to the country-specific URL
  layer.on('click', () => {
    window.location.href = `/jurisdiction/${countryName.toLowerCase()}`
  })
}

// Fetch GeoJSON data and country coverage data
onMounted(async () => {
  try {
    // Example: Fetch GeoJSON data
    const geoJsonResponse = await fetch('/temp_custom.geo.json')
    if (!geoJsonResponse.ok) throw new Error('Failed to fetch GeoJSON file')
    geoJsonData.value = await geoJsonResponse.json()

    // Example: Fetch covered countries
    const countriesResponse = await fetch('/temp_answer_coverage.txt')
    if (!countriesResponse.ok) throw new Error('Failed to fetch countries file')
    const countriesText = await countriesResponse.text()
    coveredCountries.value = countriesText
      .split('\n')
      .map((line) => line.trim())
  } catch (error) {
    console.error(error)
  }
})

// Cleanup when component is unmounted
onUnmounted(() => {
  // Reset GeoJSON data and map key to force reinitialization
  geoJsonData.value = null
  coveredCountries.value = []
  mapKey.value = Date.now() // Update key to force re-render
})
</script>

<style scoped>
.info {
  position: absolute;
  z-index: 1000;
  background: white;
  font-family: 'Inter', Arial, sans-serif; /* Replace with your global font */
}
</style>
