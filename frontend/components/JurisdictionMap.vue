<template>
  <UCard class="cold-ucard">
    <div class="popular-searches-container">
      <h2 class="popular-title">Number of Court Decisions</h2>
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
import 'leaflet/dist/leaflet.css'
</script>
