<template>
  <BaseMap
    :zoom="4"
    :center="[55, 18]"
    :enable-dragging="true"
    :max-bounds="[
      [35, -15],
      [75, 45],
    ]"
    :max-bounds-viscosity="1.0"
  />
</template>

<script setup>
import BaseMap from "./BaseMap.vue";
</script>
