<template>
  <BaseMap
    :zoom="2.5"
    :center="[4, 120]"
    :enable-dragging="true"
    :max-bounds="[[-50, 60], [70, 180]]"
    :max-bounds-viscosity="1.0"
    :background-bounds="[[-120, -200], [90, 220]]"
  />
</template>

<script setup>
import BaseMap from './BaseMap.vue'
</script>
