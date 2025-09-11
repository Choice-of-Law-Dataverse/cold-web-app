<template>
  <BaseMap
    :zoom="4"
    :center="[25, 20]"
    :enable-dragging="true"
    :max-bounds="[[10, -20], [40, 65]]"
    :max-bounds-viscosity="1.0"
  />
</template>

<script setup>
import BaseMap from './BaseMap.vue'
</script>
