<template>
  <ResultCard card-type="Loading" :result-data="{}">
    <div class="mb-3 mt-4 space-y-3">
      <USkeleton class="h-3 w-[40px] rounded-none bg-cold-gray-alpha" />
      <USkeleton class="h-4 w-[310px] rounded-none bg-cold-gray-alpha" />
      <USkeleton class="h-4 w-[280px] rounded-none bg-cold-gray-alpha" />
    </div>
  </ResultCard>
</template>

<script setup>
import ResultCard from '@/components/search-results/ResultCard.vue'
</script>
