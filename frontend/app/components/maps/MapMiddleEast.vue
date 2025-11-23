<template>
  <BaseMap
    :zoom="4"
    :center="[30, 40]"
    :enable-dragging="true"
    :max-bounds="[
      [10, 25],
      [50, 65],
    ]"
    :max-bounds-viscosity="1.0"
  />
</template>

<script setup>
import BaseMap from "./BaseMap.vue";
</script>
