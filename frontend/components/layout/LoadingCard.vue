<template>
  <ResultCard cardType="Loading" :resultData="{}">
    <div class="space-y-3 mt-4 mb-3">
      <USkeleton
        class="h-3 w-[40px] rounded-none"
        style="background-color: var(--color-cold-gray-alpha)"
      />
      <USkeleton
        class="h-4 w-[310px] rounded-none"
        style="background-color: var(--color-cold-gray-alpha)"
      />
      <USkeleton
        class="h-4 w-[280px] rounded-none"
        style="background-color: var(--color-cold-gray-alpha)"
      />
    </div>
  </ResultCard>
</template>

<script setup>
import ResultCard from '@/components/search-results/ResultCard.vue'
</script>
