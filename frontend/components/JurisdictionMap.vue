<template>
  <UCard class="cold-ucard">
    <div class="popular-searches-container">
      <h2 class="popular-title">Number of Court Decisions</h2>
      <div style="height: 50vh; width: 50vw">
        <!-- Basic Leaflet Map -->
        <LMap
          ref="map"
          :zoom="10"
          :center="[47.21322, -1.559482]"
          :use-global-leaflet="false"
        >
          <LTileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&amp;copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
            layer-type="base"
            name="OpenStreetMap"
          />
        </LMap>
      </div>

      <div style="height: 50vh; width: 50vw; margin-top: 50px">
        <!-- Overlay Leaflet Map -->
        <LMap
          ref="map"
          :zoom="4"
          :center="[37.8, -96]"
          :use-global-leaflet="false"
          :options="{
            zoomControl: false,
            scrollWheelZoom: false,
            attributionControl: false,
            dragging: false,
          }"
        >
          <!-- Tile Layer -->
          <LTileLayer
            url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            :attribution="'&copy; OpenStreetMap contributors'"
            :max-zoom="19"
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
//import { ref, onMounted } from 'vue'
//import 'leaflet/dist/leaflet.css'

// const geoJsonData = ref(null)

// Style function for GeoJSON
const style = (feature) => {
  return {
    fillColor: '#800026', // Dark red color
    weight: 2,
    opacity: 1,
    color: 'white',
    dashArray: '3',
    fillOpacity: 0.7,
  }
}

// onEachFeature function for dynamic styles and interactivity
const onEachFeature = (feature, layer) => {
  // Bind a tooltip or popup to each feature
  //layer.bindTooltip(feature.properties.name || 'Unnamed Feature')

  // Apply conditional styling
  if (feature.properties.name === 'Specific Name') {
    layer.setStyle({ fillColor: '#f7941d', weight: 2, fillOpacity: 0.7 })
  } else {
    layer.setStyle({ fillColor: '#6F4DFA', weight: 0, fillOpacity: 1 })
  }
}

// Map options to disable interactions
const mapOptions = {
  zoomControl: false, // Disable zoom control buttons
  scrollWheelZoom: false, // Disable zooming with the mouse wheel
  doubleClickZoom: false, // Disable zooming by double-clicking
  dragging: false, // Disable panning
  touchZoom: false, // Disable touch-based zooming
  keyboard: false, // Disable keyboard controls
  boxZoom: false, // Disable zooming by drawing a box
  tap: false, // Disable touch-based interactions
}

// onMounted(async () => {
//   // Fetch the GeoJSON data
//   const response = await fetch(
//     'https://leafletjs.com/examples/choropleth/us-states.js'
//   )
//   const jsonpData = await response.text()

//   // Convert JSONP to JSON by extracting the object
//   const jsonString = jsonpData.match(/{.*}/s)[0]
//   geoJsonData.value = JSON.parse(jsonString)
// })

const geoJsonData = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: { density: 100 },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-102.05, 40],
            [-102.05, 37],
            [-94.61, 37],
            [-94.61, 40],
            [-102.05, 40],
          ],
        ],
      },
    },
    // More features...
  ],
}
</script>
