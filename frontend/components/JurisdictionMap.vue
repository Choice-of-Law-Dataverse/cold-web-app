<template>
  <UCard class="cold-ucard">
    <div class="popular-searches-container">
      <h2 class="popular-title">Answer Coverage</h2>

      <div style="height: 700px; width: 100%; margin-top: 50px">
        <!-- Overlay Leaflet Map -->
        <LMap
          ref="map"
          :zoom="1.5"
          :center="[40, 0]"
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
            url="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png"
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
//url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
//import { ref, onMounted } from 'vue'
//import 'leaflet/dist/leaflet.css'

const geoJsonData = ref(null)

// Style function for GeoJSON
// const style = (feature) => {
//   return {
//     fillColor: '#800026', // Dark red color
//     weight: 2,
//     opacity: 1,
//     color: 'white',
//     dashArray: '3',
//     fillOpacity: 0.7,
//   }
// }

// onEachFeature function for dynamic styles and interactivity
const onEachFeature = (feature, layer) => {
  // Bind a tooltip or popup to each feature
  //layer.bindTooltip(feature.properties.name || 'Unnamed Feature')
  layer.setStyle({
    fillColor: '#6F4DFA',
    weight: 1,
    color: 'white',
    fillOpacity: 1,
  })

  // Apply conditional styling
  // if (feature.properties.name === 'Specific Name') {
  //   layer.setStyle({ fillColor: '#f7941d', weight: 2, fillOpacity: 0.7 })
  // } else {
  //   layer.setStyle({ fillColor: '#6F4DFA', weight: 0, fillOpacity: 1 })
  // }
}

// Map options to disable interactions
// const mapOptions = {
//   zoomControl: false, // Disable zoom control buttons
//   scrollWheelZoom: false, // Disable zooming with the mouse wheel
//   doubleClickZoom: false, // Disable zooming by double-clicking
//   dragging: false, // Disable panning
//   touchZoom: false, // Disable touch-based zooming
//   keyboard: false, // Disable keyboard controls
//   boxZoom: false, // Disable zooming by drawing a box
//   tap: false, // Disable touch-based interactions
// }

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

// const geoJsonData = {
//   type: 'FeatureCollection',
//   features: [
//     {
//       type: 'Feature',
//       properties: { density: 100 },
//       geometry: {
//         type: 'Polygon',
//         coordinates: [
//           [
//             [-102.05, 40],
//             [-102.05, 37],
//             [-94.61, 37],
//             [-94.61, 40],
//             [-102.05, 40],
//           ],
//         ],
//       },
//     },
//     // More features...
//   ],
// }
</script>
