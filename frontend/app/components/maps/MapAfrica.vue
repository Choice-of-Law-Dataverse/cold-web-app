<template>
  <BaseMap
    :zoom="3"
    :center="[4, 20]"
    :enable-dragging="true"
    :max-bounds="[
      [-40, -25],
      [40, 55],
    ]"
    :max-bounds-viscosity="1.0"
  />
</template>

<script setup>
import BaseMap from "./BaseMap.vue";
</script>
