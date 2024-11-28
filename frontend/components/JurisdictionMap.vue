<template>
  <UCard class="cold-ucard">
    <div class="popular-searches-container">
      <h2 class="popular-title">Answer Coverage</h2>

      <div style="height: 600px; width: 100%; margin-top: 50px">
        <!-- Overlay Leaflet Map -->
        <LMap
          ref="map"
          :zoom="1.5"
          :center="[35, 0]"
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
    </div>
  </UCard>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const geoJsonData = ref(null)
const blueCountries = ref([]) // List of countries to color blue by ISO3 code
const isDataReady = computed(
  () => geoJsonData.value && blueCountries.value.length > 0
)

const onEachFeature = (feature, layer) => {
  const isoCode = feature.properties.adm0_a3 // Get the ISO3 code
  const isBlue = blueCountries.value.includes(isoCode)
  //console.log('Feature ISO Code:', isoCode) // Debugging
  //console.log('Is Blue:', blueCountries.value.includes(isoCode)) // Debugging

  layer.setStyle({
    fillColor: isBlue ? 'blue' : 'var(--color-cold-cream)', // Blue for listed countries
    weight: 1,
    color: 'white',
    fillOpacity: 1,
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

  // Fetch the list of countries to color blue
  const countriesResponse = await fetch('/temp_answer_coverage.txt')
  if (!countriesResponse.ok) {
    console.error(
      'Failed to fetch countries file:',
      countriesResponse.statusText
    )
    return
  }
  const countriesText = await countriesResponse.text()
  blueCountries.value = countriesText.split('\n').map((line) => line.trim())
  //console.log('Loaded blueCountries:', blueCountries.value) // Debugging
})
</script>
