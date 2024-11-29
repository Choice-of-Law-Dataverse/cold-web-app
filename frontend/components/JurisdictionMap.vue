<template>
  <UCard class="cold-ucard">
    <div class="popular-searches-container">
      <h2 class="popular-title">Answer Coverage</h2>

      <div style="height: 600px; width: 100%; margin-top: 50px">
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
      <USelectMenu
        class="w-72 lg:w-96"
        placeholder="Select a Region"
        size="xl"
        :options="regionOptions"
        v-model="selectedRegion"
      />
    </div>
  </UCard>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const geoJsonData = ref(null)
const coveredCountries = ref([]) // List of countries to color by ISO3 code
const isDataReady = computed(
  () => geoJsonData.value && coveredCountries.value.length > 0
)

// Reactive variables for map zoom and center
const zoom = ref(1.5)
const center = ref([35, 0])
const selectedRegion = ref(null)

// List of regions with associated zoom and center
const regionOptions = [
  { label: 'World', value: { zoom: 1.5, center: [35, 0] } },
  { label: 'North America', value: { zoom: 3, center: [40, -100] } },
  { label: 'Europe', value: { zoom: 4, center: [50, 10] } },
  { label: 'Asia', value: { zoom: 3.5, center: [40, 100] } },
  { label: 'Africa', value: { zoom: 3.5, center: [0, 20] } },
  { label: 'South America', value: { zoom: 4, center: [-30, -90] } },
]

// Watch selectedRegion to update map zoom and center
watch(selectedRegion, (newRegion) => {
  if (newRegion?.value) {
    zoom.value = newRegion.value.zoom
    center.value = newRegion.value.center
  }
})

// Initialize selected region to default
selectedRegion.value = regionOptions[0]

const onEachFeature = (feature, layer) => {
  const isoCode = feature.properties.adm0_a3 // Get the ISO3 code
  const countryName = feature.properties.name // Get the country's name
  const isCovered = coveredCountries.value.includes(isoCode)

  layer.setStyle({
    fillColor: isCovered
      ? 'var(--color-cold-purple)'
      : 'var(--color-cold-gray)',
    weight: 0.5,
    color: 'white',
    fillOpacity: 1,
  })

  // Add a tooltip with the country's name
  layer.bindTooltip(countryName, {
    permanent: false, // Show only on hover
    direction: 'top', // Tooltip direction
  })

  // Add a click event to navigate to the country-specific URL
  layer.on('click', () => {
    window.location.href = `/jurisdiction/${countryName.toLowerCase()}`
  })
}

onMounted(async () => {
  // Fetch the GeoJSON data
  const geoJsonResponse = await fetch('/temp_custom.geo.json')
  if (!geoJsonResponse.ok) {
    console.error('Failed to fetch GeoJSON file:', geoJsonResponse.statusText)
    return
  }
  geoJsonData.value = await geoJsonResponse.json()

  // Fetch the list of countries to color
  const countriesResponse = await fetch('/temp_answer_coverage.txt')
  if (!countriesResponse.ok) {
    console.error(
      'Failed to fetch countries file:',
      countriesResponse.statusText
    )
    return
  }
  const countriesText = await countriesResponse.text()
  coveredCountries.value = countriesText.split('\n').map((line) => line.trim())
})
</script>
