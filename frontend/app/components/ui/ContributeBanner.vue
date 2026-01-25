<template>
  <NuxtLink
    to="/contact"
    class="group from-cold-cream/80 via-cold-cream to-cold-cream/80 hover:from-cold-cream hover:via-amber-50 hover:to-cold-cream relative block overflow-hidden rounded-b-lg bg-gradient-to-r px-6 py-5 transition-all duration-300 sm:px-8"
  >
    <!-- Subtle animated gradient overlay -->
    <div
      class="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100"
      style="animation: shimmer 2s infinite; background-size: 200% 100%"
    />

    <div class="relative flex items-center justify-between">
      <!-- Text content -->
      <div class="flex items-center gap-3">
        <div
          class="bg-cold-purple/15 group-hover:bg-cold-purple/25 flex h-8 w-8 items-center justify-center rounded-full transition-all duration-300 group-hover:scale-110"
        >
          <UIcon
            name="i-heroicons-hand-raised"
            class="text-cold-purple h-4 w-4"
          />
        </div>
        <div class="flex flex-col">
          <span
            class="text-cold-purple text-xs font-semibold tracking-wide uppercase"
          >
            Help Us Grow
          </span>
          <span
            class="group-hover:text-cold-purple text-sm font-semibold text-gray-700 transition-colors duration-300"
          >
            Contribute data for {{ jurisdictionName }}
          </span>
        </div>
      </div>

      <!-- Arrow CTA -->
      <div class="flex items-center gap-4">
        <span
          class="text-cold-purple hidden text-sm font-medium sm:block"
        >
          Get in touch
        </span>
        <div
          class="bg-cold-purple/10 group-hover:bg-cold-purple flex h-8 w-8 items-center justify-center rounded-full transition-all duration-300 group-hover:translate-x-1 group-hover:shadow-lg"
        >
          <UIcon
            name="i-heroicons-arrow-right-20-solid"
            class="text-cold-purple h-4 w-4 transition-colors duration-300 group-hover:text-white"
          />
        </div>
      </div>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
defineProps<{
  jurisdictionName: string;
}>();
</script>

<style scoped>
@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
</style>
