<template>
  <UCard class="cold-ucard">
    <div class="popular-searches-container">
      <h2 class="popular-title">Number of Court Decisions</h2>
      <div style="height: 50vh; width: 50vw">
        <!-- Leaflet Map -->
        <LMap
          ref="map"
          :zoom="zoom"
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
      <div style="height: 100vh; width: 100vw">
        <!-- Leaflet Map -->
        <LMap
          :zoom="13"
          :center="[51.505, -0.09]"
          style="height: 100%; width: 100%"
        >
          <!-- Tile Layer -->
          <LTileLayer
            url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            :attribution="'&copy; OpenStreetMap contributors'"
          />
        </LMap>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { ref } from 'vue'
import 'leaflet/dist/leaflet.css'
const zoom = ref(6)
</script>
