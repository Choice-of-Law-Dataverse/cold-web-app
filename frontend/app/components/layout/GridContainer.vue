<template>
  <div
    class="grid-container-mobile col-span-12 grid grid-cols-1 gap-6 md:grid-cols-12"
  >
    <slot />
  </div>
</template>

<style scoped>
@media (max-width: 768px) {
  .grid-container-mobile {
    max-width: 100%;
    overflow-x: hidden;
  }

  .grid-container-mobile {
    gap: 1rem !important;
  }
}

@media (max-width: 480px) {
  .grid-container-mobile {
    gap: 0.75rem !important;
  }
}
</style>
