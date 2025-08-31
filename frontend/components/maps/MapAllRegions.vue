<template>
  <!-- Overlay Leaflet Map -->
  <LMap
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// GeoJSON data and readiness state
const geoJsonData = ref(null)
const coveredCountries = ref([]) // Example: Country coverage data
const isDataReady = computed(
  () => geoJsonData.value && coveredCountries.value.length > 0
)

// Map configuration
const zoom = ref(1.5)
const center = ref([35, 0])

defineProps({
  zoom: Number,
  center: Array,
})

// Example function for handling GeoJSON features
const onEachFeature = (feature, layer) => {
  const isoCode = feature.properties.iso_a3_eh // Get the ISO3 code
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
</script>
