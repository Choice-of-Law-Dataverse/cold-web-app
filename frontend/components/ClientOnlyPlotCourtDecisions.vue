<template>
  <ClientOnly>
    <PlotCourtDecisionsJurisdiction />
    <template #fallback>
      <UCard class="cold-ucard">
        <h2 class="popular-title">Court Decisions by Jurisdiction</h2>
        <p class="result-value-small">Loading chart...</p>
        <div class="min-h-96 flex items-center justify-center">
          <div class="text-gray-500">Chart loading...</div>
        </div>
      </UCard>
    </template>
  </ClientOnly>
</template>