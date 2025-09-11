<template>
  <BaseMap
    :zoom="3"
    :center="[-20, -60]"
    :enable-dragging="true"
    :max-bounds="[
      [-60, -85],
      [15, -30],
    ]"
    :max-bounds-viscosity="1.0"
  />
</template>

<script setup>
import BaseMap from './BaseMap.vue'
</script>
