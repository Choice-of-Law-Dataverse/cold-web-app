<template>
  <div
    class="grid-container-mobile col-span-12 grid grid-cols-1 gap-x-6 md:grid-cols-12"
  >
    <slot />
  </div>
</template>

<script setup>
// This component provides a consistent grid container for landing page sections
</script>

<style scoped>
/* Ensure grid doesn't cause overflow on mobile */
@media (max-width: 768px) {
  .grid-container-mobile {
    max-width: 100%;
    overflow-x: hidden;
  }
}
</style>
