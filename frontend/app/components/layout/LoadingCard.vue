<template>
  <ResultCard card-type="Loading" :result-data="{}">
    <div class="mt-4 mb-3 space-y-3">
      <USkeleton class="bg-cold-gray-alpha h-3 w-[40px] rounded-none" />
      <USkeleton class="bg-cold-gray-alpha h-4 w-[310px] rounded-none" />
      <USkeleton class="bg-cold-gray-alpha h-4 w-[280px] rounded-none" />
    </div>
  </ResultCard>
</template>

<script setup>
import ResultCard from "@/components/search-results/ResultCard.vue";
</script>
