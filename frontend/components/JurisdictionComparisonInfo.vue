<template>
  <UCard class="cold-ucard-info">
    <!-- Main content section with reused styles -->
    <div class="main-content-grid">
      <div class="grid-item">
        <p class="result-value-small">
          <ContentDoc path="/jurisdiction_comparison_info" />
        </p>
      </div>
    </div>
  </UCard>
</template>

<style scoped>
.result-value-small :deep(p) {
  margin-bottom: 12px !important;
}

/* Reuse styles from your other component */
.main-content-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr)); /* 12-column layout */
  column-gap: var(--gutter-width); /* Match your existing gutter width */
  padding: 0px 0px 0px 32px; /* Optional padding to match card's interior */
}

.grid-item {
  grid-column: 1 / span 6; /* Spans 6 out of 12 columns */
}

.cold-ucard-info ::v-deep(.px-4) {
  padding-left: 0 !important;
  padding-right: 0 !important;
}

.cold-ucard-info ::v-deep(.py-5) {
  padding-top: 24px !important;
  padding-bottom: 12px !important;
}

.cold-ucard-info ::v-deep(.sm\:px-6) {
  padding-left: 16px !important;
  padding-right: 16px !important;
}
</style>
