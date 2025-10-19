<template>
  <div
    class="grid-container-mobile col-span-12 grid grid-cols-1 gap-6 md:grid-cols-12"
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

  /* Reduce gap on mobile to prevent card border cutoff */
  .grid-container-mobile {
    gap: 1rem !important;
  }
}

/* Further reduce gap on very small screens */
@media (max-width: 480px) {
  .grid-container-mobile {
    gap: 0.75rem !important;
  }
}
</style>
