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
            v-if="geoJsonData"
            :geojson="geoJsonData"
            :options="{ onEachFeature }"
          />
        </LMap>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const geoJsonData = ref(null)

const onEachFeature = (feature, layer) => {
  layer.setStyle({
    fillColor: '#6F4DFA',
    weight: 1,
    color: 'white',
    fillOpacity: 1,
  })
}

onMounted(async () => {
  // Fetch the GeoJSON data from the public folder
  const response = await fetch('/temp_custom.geo.json')
  if (!response.ok) {
    console.error('Failed to fetch GeoJSON file:', response.statusText)
    return
  }
  // Parse the JSON data
  geoJsonData.value = await response.json()
})
</script>
