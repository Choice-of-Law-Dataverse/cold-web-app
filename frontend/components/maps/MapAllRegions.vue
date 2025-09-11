<template>
  <BaseMap
    :zoom="1.5"
    :center="[35, 0]"
    :enable-dragging="true"
    :max-bounds="[[-90, -180], [90, 180]]"
    :max-bounds-viscosity="1.0"
  />
</template>

<script setup>
import BaseMap from './BaseMap.vue'
</script>
