<template>
  <div class="flex flex-row space-x-4 mb-8 mt-8">
    <USkeleton
      v-for="n in 3"
      :key="n"
      class="h-8 w-8 rounded-full"
      :style="{ backgroundColor: 'var(--color-cold-gray-alpha)' }"
    />
  </div>
</template>
