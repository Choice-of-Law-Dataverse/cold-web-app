<template>
  <BaseMap
    :zoom="3"
    :center="[50, -100]"
    :enable-dragging="true"
    :max-bounds="[[15, -170], [85, -50]]"
    :max-bounds-viscosity="1.0"
  />
</template>

<script setup>
import BaseMap from './BaseMap.vue'
</script>
