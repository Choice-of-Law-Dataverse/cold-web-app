<template>
  <ResultCard cardType="Legal Instrument">
    <div class="flex items-center space-x-4">
      <USkeleton class="h-12 w-12" :ui="{ rounded: 'rounded-full' }" />
      <div class="space-y-2">
        <USkeleton class="h-4 w-[250px]" />
        <USkeleton class="h-4 w-[200px]" />
      </div>
    </div>
  </ResultCard>
</template>

<script setup>
import ResultCard from '@/components/search-results/ResultCard.vue'
</script>
